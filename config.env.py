from os import environ

# Flask Configuration
DEBUG = environ.get("RANKER_DEBUG", False)
IP = environ.get("RANKER_IP", "localhost")
PORT = environ.get("RANKER_PORT", "6969")
SERVER_NAME = environ.get("RANKER_SERVER_NAME", IP + ":" + PORT)
SECRET_KEY = environ.get("RANKER_SECRET_KEY", "REPLACE_THIS")

# SSO Configuration
OIDC_AUTHORITY = environ.get("RANKER_OIDC_AUTHORITY", "https://sso.csh.rit.edu/auth/")
OIDC_CLIENT_ID = environ.get("RANKER_OIDC_CLIENT_ID", "ranker")
OIDC_CLIENT_SECRET = environ.get("RANKER_OIDC_CLIENT_SECRET")
OIDC_REALM = environ.get("RANKER_OIDC_REALM", "csh")
OIDC_SCOPES = {"scope": "openid email profile:twitter profile:twitch"}

# SQLAlchemy Configuration
SQLALCHEMY_DATABASE_URI = environ.get("RANKER_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis Configuration
REDIS_HOST = environ.get("RANKER_REDIS_HOST", "127.0.0.1")
REDIS_PORT = environ.get("RANKER_REDIS_PORT", "6379")
REDIS_DB = environ.get("RANKER_REDIS_DB", 0)
REDIS_PASS = environ.get("RANKER_REDIS_PASS", None)

# Slack Configuration
SLACK_ENABLED = environ.get("RANKER_SLACK_ENABLED", False)
SLACK_API_KEY = environ.get("RANKER_SLACK_API_KEY", None)

# Application-Specific Configuration
RATING_IMPACT_CONSTANT = int(environ.get("RANKER_RATING_IMPACT_CONSTANT", 32))
RATING_DEFAULT = int(environ.get("RANKER_RATING_DEFAULT", 100))


# Profile Creation Configuration
PROFILE_IMAGES_ROOT = environ.get("RANKER_PROFILE_IMAGES_ROOT", "https://profiles.csh.rit.edu")

# Set to false if performing a flask migration or audit
ENABLE_API = environ.get("RANKER_ENABLE_API", False)
