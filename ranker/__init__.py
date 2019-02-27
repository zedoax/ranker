import os

import csh_ldap
from flask import Flask
from flask_migrate import Migrate
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Load Configuration
_root_dir = os.path.dirname(os.path.realpath(__name__))
app.config.from_pyfile(os.path.join(_root_dir, "config.env.py"))

# Load Custom Configurations
_conf_file = os.path.join(_root_dir, "config.py")
if os.path.exists(_conf_file):
    app.config.from_pyfile(_conf_file)

# Load SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Load CSH Authentication
auth = OIDCAuthentication(app, issuer=app.config["OIDC_ISSUER"], client_registration_info={
    "client_id": app.config["OIDC_CLIENT_ID"],
    "client_secret": app.config["OIDC_CLIENT_SECRET"],
    "post_logout_redirect_uris": "/logout/"
})

_ldap = csh_ldap.CSHLDAP(app.config["LDAP_BIND_DN"], app.config["LDAP_BIND_PASS"])

from ranker.routes import ranking, api
