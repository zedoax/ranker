from functools import wraps

from ranker.auth import auth
from ranker.auth import ldap
from flask import session
from ranker import app


def ldap_get_member_slack(username):
    """ Return CSH user based on slack username """
    return ldap.get_member_slackuid(username)


def ldap_get_member(username):
    """ Return CSH user based on ldap username """
    return ldap.get_member(username, uid=True)


def ranker_auth(func):
    """ Decorator for ldap authentication """
    @auth.oidc_auth('app')
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        session['username'] = str(session['userinfo'].get('preferred_username', ''))
        return func(*args, **kwargs)

    return wrapped_function
