from ranker import app
from ranker.auth import oidc


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
