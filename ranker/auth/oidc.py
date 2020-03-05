from requests.auth import AuthBase

from ranker.auth import oidc


class Oidc:
    @staticmethod
    def user_by_token(bearer):
        user = oidc.introspect(Oidc.strip_bearer_token(bearer))
        if not user["active"]:
            return False
        return user["preferred_username"]
        # return {
        #     "username": user["preferred_username"],
        #     "first_name": user["given_name"],
        #     "last_name": user["family_name"],
        #     "profile_img": "{0}/image/{1}".format(app.config["PROFILE_IMAGES_ROOT"], user["preferred_username"])
        # }

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
