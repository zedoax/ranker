import logging

from flask import make_response, Blueprint, g
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ranker import app
from ranker.api.utils import get_request_json, auth_required, witness_required
from ranker.api.utils import make_response
from ranker.db.match import Match
from ranker.db.score import Score
from ranker.db.season import Season
from ranker.db.user import User
from ranker.db.utils import create_score, create_match, validate_rounds
from ranker.redis.redis import put_challenge, accept_challenge, del_challenge, pop_challenge
from ranker.schema.accept import accept_schema
from ranker.schema.cancel import cancel_schema
from ranker.schema.challenge import challenge_schema
from ranker.schema.match import matches_schema, match_schema
from ranker.schema.witness import witness_schema

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
        content = get_request_json(challenge_schema)
        content["challenger"] = g.user.username
    except ValidationError as error:
        logging.error('Error: Challenge request failed: ', error)
        return make_response("Sorry, that's not a valid challenge statement", 400)

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
        content = get_request_json(accept_schema)
        content["challenged"] = g.user.username
    except ValidationError as error:
        logging.error('Error: Accept request failed: ', error)
        return make_response("Sorry, that's not a valid acceptance statement", 400)

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
        logging.error("Error: Could not accept challenge: ", err)
        return make_response("Hmm.. Looks like you are not being challenged", 400)
    return make_response("You have accepted {0}'s challenge".format(challenger.username), 200)


@match_bp.route("/cancel", methods=["POST"])
@auth_required
def cancel_match():
    try:
        content = get_request_json(cancel_schema)
        content['challenged' if 'challenged' not in content else 'challenger'] = g.user.username
    except ValidationError as error:
        logging.error('Error: Cancel request failed: ', error)
        return make_response("Sorry, that's not a valid cancellation statement", 400)

    challenger = User.get_user(username=content["challenger"])
    challenged = User.get_user(username=content["challenged"])

    if not challenger:
        return make_response("You have not yet logged into ranker", 400)
    if not challenged:
        return make_response("That challenger has not yet logged into ranker", 400)
    if challenger == challenged:
        return make_response("You cannot even challenge yourself, wtf are you doing??", 400)

    try:
        del_challenge(challenger.username, challenged.username)
    except ValueError as err:
        logging.error("Error: Could not cancel challenge: ", err)
        return make_response("Hmm.. Looks like you're not challenging each other", 400)
    return make_response("You have cancelled {0}'s challenge".format(content["challenger"]), 200)


@match_bp.route("/witness", methods=["POST"])
@auth_required
@witness_required
def witness_match():
    try:
        content = get_request_json(witness_schema)
    except ValidationError as error:
        logging.error('Error: Witness request failed: ', error)
        return make_response("Sorry, that's not a valid witness statement", 400)

    try:
        content["season"], content["challenger"] = pop_challenge(content["winner"], content["loser"])
    except ValueError as err:
        logging.error("Error: Witness request failed: ", err)
        return make_response("There's not challenge ongoing between those two players", 400)
    except PermissionError as err:
        logging.error("Error: Witness request failed: ", err)
        return make_response("That challenge has not been accepted", 400)

    season = Season.get_season(content["season"])
    winner = Score.get_score(username=content['winner'], season=season.id)
    loser = Score.get_score(username=content['loser'], season=season.id)
    witness = User.get_user(username=content['witness'])
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

    try:
        validate_rounds(winner_wins, loser_wins, season.game.max_rounds, season.game.min_rounds)
    except ValueError as error:
        make_response(error, 400)

    try:
        create_match(winner, loser, witness, season, winner_wins, loser_wins, content["challenger"])
    except SQLAlchemyError as error:
        logging.error("Could not insert match into database: ", error)
        return make_response("Sorry, something went wrong!", 500)
    return make_response("Your match has been accepted!", 200)
