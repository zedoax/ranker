from datetime import datetime

from dateutil import parser as date
from flask import Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ranker import logging
from ranker.api.utils import get_request_json, make_response, admin_required, auth_required
from ranker.db import games, matches, scores, seasons
from ranker.db.utils import create_season
from ranker.schema.db import seasons_schema, season_schema, matches_schema
from ranker.schema.api import season_schema as api_season_schema

season_bp = Blueprint("seasons", __name__, url_prefix="/seasons")


@season_bp.route("", methods=["GET"])
def get_seasons():
    _seasons = seasons.get_season()
    return seasons_schema.dumps(_seasons)


@season_bp.route("/active", methods=["GET"])
def get_seasons_active():
    _seasons = seasons.get_season(date=datetime.now())
    return seasons_schema.dumps(_seasons)


@season_bp.route("/<int:_id>", methods=["GET"])
def get_season(_id):
    season = seasons.get_season(_id=_id)
    return season_schema.dumps(season)


@season_bp.route("/<int:_id>/scores", methods=["GET"])
def get_season_scores(_id):
    season = seasons.get_season(_id=_id)
    _scores = scores.get_score(season=season.id)
    return seasons_schema.dumps(_scores)


@season_bp.route("/<int:_id>/matches", methods=["GET"])
def get_season_matches(_id):
    season = seasons.get_season(_id=_id)
    _matches = matches.get_match(season=season.id)
    return matches_schema.dumps(_matches)


@season_bp.route("/new", methods=["POST"])
@auth_required
@admin_required
def new_season():
    try:
        content = get_request_json(api_season_schema)
    except ValidationError as error:
        return make_response(error, 400)

    name = content["name"]
    banner = content["banner"]
    game = games.get_game(content["game"])
    start = date.parse(content["start"])
    end = date.parse(content["end"])

    if not game:
        return make_response("Sorry, couldn't find that game", 404)

    try:
        create_season(name, banner, game, start, end)
    except SQLAlchemyError as err:
        logging.error("Error: Could not create season: ", err)
        return make_response("Sorry, that season could not be created. Check your fields and try again", 400)
    return make_response("You have created the season: {0}".format(name), 200)
