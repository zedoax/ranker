""" Utils module """

from functools import wraps

from flask import session
from ranker import _ldap


def before_request(func):
    """ Pre-processing to be done before a request """
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


def ldap_get_member_slack(username):
    """ Return CSH user based on slack username """
    return _ldap.get_member_slackuid(username)


def ldap_get_member(username):
    """ Return CSH user based on ldap username """
    return _ldap.get_member(username, uid=True)
