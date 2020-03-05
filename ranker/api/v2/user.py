from flask import Blueprint, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ranker import app, logging
from ranker.api.utils import make_response, auth_required, get_request_json
from ranker.db import seasons, users
from ranker.db.user import User
from ranker.db.utils import create_user as _create_user
from ranker.schema.db import seasons_schema, users_schema, user_schema
from ranker.schema.api import user_schema as new_user_schema

config = app.config
user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("", methods=["GET"])
def get_users():
    _users = users.get_user()
    return users_schema.dumps(users)


@user_bp.route("/<username>", methods=["GET"])
def get_user(username):
    user = User.get_user(username=username)
    return user_schema.dumps(user)


@user_bp.route("/<username>/seasons", methods=["GET"])
def get_user_seasons(username):
    _seasons = seasons.get_season(username=username)
    return seasons_schema.dumps(_seasons)


@user_bp.route("/<username>/witness", methods=["GET"])
def get_user_is_witness(username):
    user = User.get_user(username=username)
    if not user:
        return jsonify(witness=False)
    return jsonify(witness=user.witness)


@user_bp.route("/<username>/admin", methods=["GET"])
def get_user_is_admin(username):
    user = User.get_user(username=username)
    if not user:
        return jsonify(admin=False)
    return jsonify(admin=user.admin)


@user_bp.route("/slack/<_id>", methods=["GET"])
def get_slack_user(_id):
    user = User.get_user(slack_id=_id)
    if not user:
        return jsonify
    return user_schema.dumps(user)


@user_bp.route("/create", methods=["POST"])
@auth_required
def create_user():
    """ Silently create user if first login """
    try:
        content = get_request_json(new_user_schema)
        _create_user(content["username"], content["first_name"], content["last_name"], content["profile_img"])
    except ValidationError as error:
        logging.error(error)
        return make_response(None, 400)
    except SQLAlchemyError as error:
        logging.error(error)
        return make_response(None, 500)
    return make_response(None, 201)
