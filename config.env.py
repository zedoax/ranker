from os import environ

# Flask Configuration
DEBUG = False
IP = environ.get("RANKER_IP", "localhost")
PORT = environ.get("RANKER_PORT", "6969")
SERVER_NAME = environ.get("RANKER_SERVER_NAME", IP + ":" + PORT)
SECRET_KEY = environ.get("RANKER_SECRET_KEY", "REPLACE_THIS")

# SSO Configuration
REALM = environ.get("RANKER_REALM", "csh")

OIDC_ISSUER = environ.get("RANKER_OIDC_ISSUER", "https://sso.csh.rit.edu/auth/realms/csh")
OIDC_CLIENT_ID = environ.get("RANKER_OIDC_CLIENT_ID", "ranker")
OIDC_CLIENT_SECRET = environ.get("RANKER_OIDC_CLIENT_SECRET", "REPLACE_THIS")

# SQLAlchemy config
SQLALCHEMY_DATABASE_URI = environ.get("RANKER_DATABASE_URI", "sqlite://")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# LDAP config
LDAP_BIND_DN = environ.get("RANKER_LDAP_BIND_DN", None)
LDAP_BIND_PASS = environ.get("RANKER_LDAP_BIND_PASS", None)
