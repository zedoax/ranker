from flask import request
from requests.auth import AuthBase

from ranker import app
from ranker.auth import oidc
from ranker.slack import bot_token


class Oidc:
    @staticmethod
    def user_by_token(bearer):
        token = Oidc.strip_bearer_token(bearer)
        if token == bot_token['bearer']:
            return request.headers.environ.get("HTTP_USERNAME")
        try:
            user = oidc.userinfo(token)
        except Exception:
            return None
        return user["preferred_username"]

    @staticmethod
    def get_user_info():
        bearer = request.headers.environ.get("HTTP_AUTHORIZATION")
        token = Oidc.strip_bearer_token(bearer)
        try:
            user = oidc.userinfo(token)
        except Exception:
            return None
        return {
            "username": user["preferred_username"],
            "first_name": user["given_name"],
            "last_name": user["family_name"],
            "profile_img": "{0}/image/{1}".format(app.config["PROFILE_IMAGES_ROOT"], user["preferred_username"])
        }

    @staticmethod
    def strip_bearer_token(bearer):
        return bearer[7:]


class OidcAuth(AuthBase):
    def __init__(self, token, username):
        self.token = token
        self.username = username

    def __call__(self, r):
        r.headers["AUTHORIZATION"] = "Bearer " + self.token
        r.headers["USERNAME"] = self.username
        return r
