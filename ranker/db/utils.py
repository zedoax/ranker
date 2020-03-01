from sqlalchemy.exc import SQLAlchemyError

from ranker.db import db
from ranker.db.game import Game
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
