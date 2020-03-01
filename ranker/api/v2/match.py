import logging

from flask import make_response, Blueprint, g
from sqlalchemy.exc import SQLAlchemyError

from ranker import app
from ranker.api.utils import convert_request, content_is_valid, auth_required, witness_required
from ranker.api.utils import make_response
from ranker.db import db
from ranker.db.match import Match
from ranker.db.score import Score
from ranker.db.season import Season
from ranker.db.user import User
from ranker.db.utils import create_score
from ranker.redis.redis import put_challenge, accept_challenge, del_challenge, pop_challenge
from ranker.schema.match import matches_schema, match_schema

config = app.config
match_bp = Blueprint("matches", __name__, url_prefix="/matches")


@match_bp.route("", methods=["GET"])
def get_user_matches():
    matches = Match.get_match()
    return matches_schema.dumps(matches)


@match_bp.route("/<int:_id>", methods=["GET"])
def get_match(_id):
    match = Match.get_match(_id=_id)
    return match_schema.dumps(match)


@match_bp.route("/new", methods=["POST"])
@auth_required
def new_match():
    try:
        content = convert_request()
        content["challenger"] = g.user.username
    except AssertionError as err:
        logging.error('Error: Challenge request failed: ', err)
        return make_response("Sorry, that's not a valid request", 400)
    if not content_is_valid(content, 'challenger', 'challenged', 'season'):
        return make_response("Sorry, that's not a valid challenge", 400)

    logging.info(content)
    challenger = User.get_user(username=content["challenger"])
    challenged = User.get_user(username=content["challenged"])
    season = Season.get_season(_id=content["season"])

    if not challenger:
        make_response("You have not yet logged into ranker", 400)
    if not challenged:
        make_response("That challenger has not yet logged into ranker", 400)
    if not season:
        make_response("That season does not exist", 400)

    if challenger == challenged:
        return make_response("You cannot challenge yourself!", 400)

    try:
        put_challenge(content["challenger"], content["challenged"], content["season"])
    except ValueError as err:
        logging.error("Error: Could not create challenge", err)
        return make_response("Hmm.. Seems like you're already challenging each other", 400)
    return make_response("You have challenged {0}".format(challenged.username), 200)


@match_bp.route("/accept", methods=["POST"])
@auth_required
def accept_match():
    try:
        content = convert_request()
        content["challenged"] = g.user.username
    except AssertionError as err:
        logging.error('Error: Accept request failed: ', err)
        return make_response("Sorry, that's not a valid request", 400)
    if not content_is_valid(content, 'challenger', 'challenged'):
        return make_response("Sorry, that's not a valid acceptance", 400)

    challenger = User.get_user(username=content["challenger"])
    challenged = User.get_user(username=content["challenged"])

    if not challenger:
        return make_response("You have not yet logged into ranker", 400)
    if not challenged:
        return make_response("That challenger has not yet logged into ranker", 400)
    if challenger == challenged:
        return make_response("You cannot accept a challenge with yourself!", 400)

    try:
        accept_challenge(challenger.username, challenged.username)
    except ValueError as err:
        logging.error("Error: Could not accept challenge", err)
        return make_response("Hmm.. Looks like you are not being challenged", 400)
    return make_response("You have accepted {0}'s challenge".format(challenger.username), 200)


@match_bp.route("/cancel", methods=["POST"])
@auth_required
def cancel_match():
    try:
        content = convert_request()
        if "challenged" not in content:
            content["challenged"] = g.user.username
        else:
            content["challenger"] = g.user.username
    except AssertionError as err:
        logging.error('Error: Accept request failed: ', err)
        return make_response("Sorry, that's not a valid request", 400)
    if not content_is_valid(content, 'challenger', 'challenged'):
        return make_response("Sorry, that's not a valid cancel", 400)

    try:
        del_challenge(content["challenger"], content["challenged"])
    except ValueError as err:
        logging.error("Error: Could not cancel challenge", err)
        return make_response("Hmm.. Looks like you're not challenging each other", 400)
    return make_response("You have cancelled {0}'s challenge".format(content["challenger"]), 200)


@match_bp.route("/witness", methods=["POST"])
@auth_required
@witness_required
def witness_match():
    try:
        content = convert_request()
    except AssertionError as err:
        logging.error('Error: Witness request failed: ', err)
        return make_response("Sorry, that's not a valid request", 400)
    if not content_is_valid(content, 'winner', 'loser', 'winner_wins', 'loser_wins', 'witness'):
        return make_response("Sorry, that's not a valid witness statement", 400)

    try:
        content["season"], content["challenger"] = pop_challenge(content["winner"], content["loser"])
    except ValueError as err:
        logging.error("Error: Witness request failed: ", err)
        return make_response("There's not challenge ongoing between those two players", 400)
    except PermissionError as err:
        logging.error("Error: Witness request failed: ", err)
        return make_response("That challenge has not been accepted", 400)

    # Get the necessary values from the request
    season = Season.get_season(content["season"])
    winner = Score.get_score(username=content['winner'], season=season.id)
    loser = Score.get_score(username=content['loser'], season=season.id)
    witness = User.get_user(content['witness'])
    winner_wins = content['winner_wins']
    loser_wins = content['loser_wins']

    if season is None:
        return make_response("Sorry, season {0} not found".format(content["season"]), 404)

    if winner is None:
        try:
            winner = create_score(content["winner"], season.id)
        except ValueError as err:
            logging.error("Error: Player score could not be generated: ", err)
            return make_response("The winner could not be added to current season", 500)
        except SQLAlchemyError as err:
            logging.error(err)
            return make_response("Something went wrong :(", 500)
    if loser is None:
        try:
            loser = create_score(content["loser"], season.id)
        except ValueError as err:
            logging.error("Error: Player score could not be generated: ", err)
            return make_response("The loser could not be added to current season", 500)
        except SQLAlchemyError as err:
            logging.error(err)
            return make_response("Something went wrong :(", 500)

    if winner is None or loser is None:
        logging.error("Error: Player not found. Winner: {0}, Loser: {1}"
                      .format(content['winner'], content['loser']))
        return make_response("Could not find the match contestants", 404)

    if winner.username == loser.username:
        return make_response("A match cannot be conducted by the same player", 400)

    if witness is None:
        return make_response("The witness could not be found", 404)
    if not witness.witness:
        return make_response("That user is not a valid witness", 400)

    # Verify the challenge rounds are legal
    if winner_wins + loser_wins > season.game.max_rounds:
        return make_response("That's too many rounds!", 400)
    if winner_wins + loser_wins < season.game.min_rounds:
        return make_response("That's not enough rounds!", 400)
    if winner_wins < int(season.game.max_rounds / 2) + 1:
        return make_response("That's not the right number of wins:losses", 400)
    if winner_wins < loser_wins:
        return make_response("The loser's score can't be higher than the winner's", 400)

    # Calculate Rating Changes
    rating_winner = pow(10, (winner.score / 400))
    rating_loser = pow(10, (loser.score / 400))

    expected_rating_winner = rating_winner / (rating_winner + rating_loser)
    expected_rating_loser = rating_loser / (rating_winner + rating_loser)

    plus_score = config['RATING_IMPACT_CONSTANT'] * (1 - expected_rating_winner)
    minus_score = config['RATING_IMPACT_CONSTANT'] * (0 - expected_rating_loser)

    try:
        match = Match(
            winner=winner,
            loser=loser,
            witness=witness,
            season=season,
            winner_wins=winner_wins,
            loser_wins=loser_wins,
            winner_prev_score=winner.score,
            loser_prev_score=loser.score,
            challenger_is_winner=winner.username == content["challenger"])
        winner.score += plus_score
        loser.score += minus_score

        db.session.add(match)
        db.session.commit()
    except SQLAlchemyError as err:
        logging.error("Could not insert match into database: ", err)
        return make_response("Sorry, something went wrong!", 500)
    return make_response("Your match has been accepted!", 200)
