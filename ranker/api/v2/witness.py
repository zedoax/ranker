from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from ranker import app, logging
from ranker.api.utils import convert_request, make_response, content_is_valid, admin_required, auth_required
from ranker.db import db
from ranker.db.user import User
from ranker.schema.user import users_schema

config = app.config
witness_bp = Blueprint("witnesses", __name__, url_prefix="/witnesses")


@witness_bp.route("", methods=["GET"])
def get_witnesses():
    witnesses = User.get_user(witness=True)
    return users_schema.dumps(witnesses)


@witness_bp.route("/new", methods=["POST"])
@auth_required
@admin_required
def new_witness():
    try:
        content = convert_request(request)
    except AssertionError as err:
        logging.error('Error: Witness request failed: ', err)
        return make_response("Sorry, that's not a valid request", 400)
    if not content_is_valid(content, 'username'):
        return make_response("Sorry, that's not a valid add witness request", 400)

    username = content["username"]

    try:
        user = User.get_user(username=username)
        user.witness = True
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as err:
        logging.error("Error: Could not create witness: ", err)
        return make_response("Sorry, that witness could not be added. Check your fields and try again", 400)
    return make_response("{0} has been made a witness".format(user.username), 200)
