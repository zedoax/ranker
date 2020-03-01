from flask import Blueprint, jsonify
from sqlalchemy.exc import SQLAlchemyError

from ranker import app, logging
from ranker.api.utils import make_response, auth_required
from ranker.db.season import Season
from ranker.db.user import User
from ranker.db.utils import create_user as _create_user
from ranker.schema.season import seasons_schema
from ranker.schema.user import users_schema, user_schema

config = app.config
user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("", methods=["GET"])
def get_users():
    users = User.get_user()
    return users_schema.dumps(users)


@user_bp.route("/<username>", methods=["GET"])
def get_user(username):
    user = User.get_user(username=username)
    return user_schema.dumps(user)


@user_bp.route("/<username>/seasons", methods=["GET"])
def get_user_seasons(username):
    seasons = Season.get_season(username=username)
    return seasons_schema.dumps(seasons)


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
def create_user(user_data=None):
    """ Silently create user if first login """
    if not user_data:
        return make_response(None, 200)
    try:
        _create_user(user_data["username"], user_data["first_name"], user_data["last_name"], user_data["profile_img"])
    except SQLAlchemyError as err:
        logging.error(err)
        return make_response(None, 500)
    return make_response(None, 201)
