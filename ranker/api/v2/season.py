from datetime import datetime

from dateutil import parser as date
from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from ranker import logging
from ranker.api.utils import convert_request, make_response, content_is_valid, admin_required, auth_required
from ranker.db.game import Game
from ranker.db.match import Match
from ranker.db.score import Score
from ranker.db.season import Season
from ranker.db.utils import create_season
from ranker.schema.match import matches_schema
from ranker.schema.season import seasons_schema, season_schema

season_bp = Blueprint("seasons", __name__, url_prefix="/seasons")


@season_bp.route("", methods=["GET"])
def get_seasons():
    seasons = Season.get_season()
    return seasons_schema.dumps(seasons)


@season_bp.route("/active", methods=["GET"])
def get_seasons_active():
    seasons = Season.get_season(date=datetime.now())
    return seasons_schema.dumps(seasons)


@season_bp.route("/<int:_id>", methods=["GET"])
def get_season(_id):
    season = Season.get_season(_id=_id)
    return season_schema.dumps(season)


@season_bp.route("/<int:_id>/scores", methods=["GET"])
def get_season_scores(_id):
    season = Season.get_season(_id=_id)
    scores = Score.get_score(season=season.id)
    return seasons_schema.dumps(scores)


@season_bp.route("/<int:_id>/matches", methods=["GET"])
def get_season_matches(_id):
    season = Season.get_season(_id=_id)
    matches = Match.get_match(season=season.id)
    return matches_schema.dumps(matches)


@season_bp.route("/new", methods=["POST"])
@auth_required
@admin_required
def new_season():
    try:
        content = convert_request()
    except AssertionError as err:
        logging.error('Error: Challenge request failed: ', err)
        return make_response("Sorry, that's not a valid request", 400)
    if not content_is_valid(content, 'name', 'banner', 'game', 'start', 'end'):
        return make_response("Sorry, that's not a valid game request", 400)

    name = content["name"]
    banner = content["banner"]
    game = Game.get_game(content["game"])
    start = date.parse(content["start"])
    end = date.parse(content["end"])

    if not Game:
        return make_response("Sorry, I couldn't find that game", 404)

    try:
        create_season(name, banner, game, start, end)
    except SQLAlchemyError as err:
        logging.error("Error: Could not create season: ", err)
        return make_response("Sorry, that season could not be created. Check your fields and try again", 400)
    return make_response("You have created the season: {0}".format(name), 200)
