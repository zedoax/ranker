from functools import wraps

from flask import g, abort
from flask import make_response as flask_make_response
from flask import request

from ranker.auth.oidc import Oidc
from ranker.db import users


def auth_required(func):
    """ Pre-processing to be done before a request """
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if not request.headers.environ.get('HTTP_AUTHORIZATION'):
            return make_response('No bearer token given', 401)
        bearer = request.headers.environ.get("HTTP_AUTHORIZATION")
        username = Oidc.user_by_token(bearer)
        if not username:
            return make_response("Unable to authenticate authorization token", 401)
        user = users.get_user(username=username)
        if not user:
            return abort('Unable to authenticate user details')
        g.user = user
        return func(*args, **kwargs)
    return wrapped_function


def admin_required(func):
    """ Performs check against auth for admin privileges """
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if not g.user:
            return make_response("You are not logged in", 401)
        if not g.user.admin:
            return make_response("You do not have permission to perform this action", 403)
        return func(*args, **kwargs)
    return wrapped_function


def witness_required(func):
    """ Performs check against auth for admin privileges """
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if not g.user:
            return make_response("You are not logged in", 401)
        if not g.user.witness:
            return make_response("You are not authorized to perform this action", 403)
        return func(*args, **kwargs)
    return wrapped_function


def make_response(message, status):
    response = flask_make_response(message, status)
    return response


def get_request_json(schema):
    schema.validate(request.get_json())
    return request.get_json()


def get_request_form(schema):
    schema.validate(request.form)
    return request.form


def content_is_valid(content, *args):
    for item in args:
        if item not in content:
            return False
    return True


def serialize_rows(rows):
    return list(map(lambda row: serialize_row(row), rows))


def serialize_row(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
