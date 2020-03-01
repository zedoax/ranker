from ranker import app
from ranker.auth import oidc
from requests.auth import AuthBase


class Oidc:
    @staticmethod
    def user_by_token(bearer):
        user = oidc.introspect(bearer[7:])
        if not user["active"]:
            return False
        return {
            "username": user["preferred_username"],
            "first_name": user["given_name"],
            "last_name": user["family_name"],
            "profile_img": "{0}/image/{1}".format(app.config["PROFILE_IMAGES_ROOT"], user["preferred_username"])
        }


class OidcAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
