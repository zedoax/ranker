from sqlalchemy.exc import SQLAlchemyError

from ranker import app
from ranker.db import db
from ranker.db.game import Game
from ranker.db.match import Match
from ranker.db.score import Score
from ranker.db.season import Season
from ranker.db.user import User


def create_season(name, banner, game, start, end):
    try:
        season = Season(
            name=name,
            banner=banner,
            game=game,
            start=start,
            end=end
        )
        db.session.add(season)
        db.session.commit()
    except SQLAlchemyError as err:
        raise err


def create_game(title, img, description, max_rounds, min_rounds):
    try:
        game = Game(
            title=title,
            img=img,
            description=description,
            max_rounds=max_rounds,
            min_rounds=min_rounds
        )
        db.session.add(game)
        db.session.commit()
    except SQLAlchemyError as err:
        raise err


def create_score(username, season_id):
    user = User.get_user(username)
    season = Season.get_season(season_id)

    if not user:
        raise ValueError("Error: Cannot create score. User '{0}' not found".format(username))
    if not season:
        raise ValueError("Error: Cannot create score. Season '{0}' not found".format(season_id))

    try:
        score = Score(
            user=user,
            season=season
        )

        db.session.add(score)
        db.session.commit()
    except SQLAlchemyError as err:
        raise err
    return score


def create_user(username, first_name, last_name, profile_img, **kwargs):
    try:
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            profile_img=profile_img,
            twitch_id=kwargs.get("twitch_id"),
            twitter_id=kwargs.get("twitter_id"),
            slack_id=kwargs.get("slack_id")
        )

        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as err:
        raise err
    return user


def create_match(winner, loser, witness, season, winner_wins, loser_wins, challenger):
    # Calculate Rating Changes
    rating_winner = pow(10, (winner.score / 400))
    rating_loser = pow(10, (loser.score / 400))

    expected_rating_winner = rating_winner / (rating_winner + rating_loser)
    expected_rating_loser = rating_loser / (rating_winner + rating_loser)

    plus_score = app.config['RATING_IMPACT_CONSTANT'] * (1 - expected_rating_winner)
    minus_score = app.config['RATING_IMPACT_CONSTANT'] * (0 - expected_rating_loser)

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
            challenger_is_winner=winner.username == challenger)
        winner.score += plus_score
        loser.score += minus_score

        db.session.add(match)
        db.session.commit()
    except SQLAlchemyError as error:
        raise error


def validate_rounds(winner_wins, loser_wins, max_rounds, min_rounds):
    if winner_wins + loser_wins > max_rounds:
        raise ValueError('That is too many rounds!')
    if winner_wins + loser_wins < min_rounds:
        raise ValueError('That is not enough rounds!')
    if winner_wins < int(max_rounds / 2) + 1:
        raise ValueError('That is not enough rounds for the winner')
    if winner_wins < loser_wins:
        raise ValueError('The loser cannot win more rounds than the winner!')
