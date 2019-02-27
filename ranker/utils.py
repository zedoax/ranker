from functools import wraps

from flask import session
from ranker import _ldap


def before_request(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        uid = str(session["userinfo"].get("preferred_username", ""))
        info = {
            "realm": session["id_token"]["iss"],
            "uid": uid
        }
        kwargs["info"] = info
        return func(*args, **kwargs)
    return wrapped_function


def ldap_get_member(username):
    return _ldap.get_member(username, uid=True)
