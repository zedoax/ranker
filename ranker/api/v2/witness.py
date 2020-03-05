from flask import Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ranker import app, logging
from ranker.api.utils import get_request_json, make_response, admin_required, auth_required
from ranker.db import db
from ranker.db.user import User
from ranker.schema.api import username_schema
from ranker.schema.db import users_schema

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
        content = get_request_json(username_schema)
    except ValidationError as error:
        return make_response(error, 400)

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
