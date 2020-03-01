""" Utils module """

from functools import wraps

from flask import jsonify, g
from flask import make_response as flask_make_response
from flask import request

from ranker.auth.oidc import Oidc
from ranker.db.user import User


def auth_required(func):
    """ Pre-processing to be done before a request """
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        token = request.headers.environ.get("HTTP_AUTHORIZATION")
        user_data = Oidc.user_by_token(token)
        if not user_data:
            return make_response("Unable to authenticate authorization token", 401)
        user = User.get_user(username=user_data["username"])
        if not user:
            return func(*args, **kwargs, user_data=user_data)
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
    response = flask_make_response(jsonify(message=message), status)
    response.headers["Set-Cookie"] = "HttpOnly;Secure;SameSite=Strict"
    return response


def convert_request():
    if not request.is_json:
        raise AssertionError('Error: Request is not in json format')
    return request.get_json()


def get_request_form(*args):
    content = []
    for arg in args:
        content.append(request.form.get(arg))
    return content


def content_is_valid(content, *args):
    for item in args:
        if item not in content:
            return False
    return True


def serialize_rows(rows):
    return list(map(lambda row: serialize_row(row), rows))


def serialize_row(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
