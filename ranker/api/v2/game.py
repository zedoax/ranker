from flask import Blueprint, g
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ranker import app, logging
from ranker.api.utils import get_request_json, make_response, admin_required, auth_required
from ranker.db.game import Game
from ranker.db.utils import create_game
from ranker.schema.db import games_schema, game_schema, seasons_schema

config = app.config
game_bp = Blueprint("game", __name__, url_prefix="/games")


@game_bp.route("", methods=["GET"])
def get_games():
    games = Game.get_game()
    return games_schema.dumps(games)


@game_bp.route("/<int:_id>", methods=["GET"])
def get_game(_id):
    game = Game.get_game(_id)
    return game_schema.dumps(game)


@game_bp.route("/<int:_id>/seasons", methods=["GET"])
def get_game_seasons(_id):
    game = Game.get_game(_id)
    seasons = game.seasons
    return seasons_schema.dumps(seasons)


@game_bp.route("/new", methods=["POST"])
@auth_required
@admin_required
def new_game():
    if not g.user.admin:
        return make_response("You are not an authorized administrator", 403)

    try:
        content = get_request_json(game_schema)
    except ValidationError as error:
        logging.error(error)
        return make_response(error, 400)

    title = content["title"]
    img = content["img"]
    description = content["description"]
    # TODO: V3 -> Implement Game Based Rounds
    max_rounds = 5
    min_rounds = 3

    try:
        create_game(title, img, description, max_rounds, min_rounds)
    except SQLAlchemyError as err:
        logging.error("Error: Could not create game: ", err)
        return make_response("Sorry, that game could not be created. Check your fields and try again", 400)
    return make_response("You have created the game: {0}".format(title), 200)
