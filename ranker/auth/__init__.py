from keycloak import KeycloakOpenID

from ranker import app

oidc = KeycloakOpenID(
    server_url=app.config["OIDC_ENDPOINT"],
    client_id=app.config["OIDC_CLIENT_ID"],
    realm_name=app.config["OIDC_REALM"],
    client_secret_key=app.config["OIDC_CLIENT_SECRET"],
    verify=True
)
