""" Ranker main module """
import logging
import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Load Configuration
_root_dir = Path(__file__).parent.parent
app.config.from_pyfile(os.path.join(_root_dir, "config.env.py"))

# Load Custom Configurations
_conf_file = os.path.join(_root_dir, "config.py")
if os.path.exists(_conf_file):
    app.config.from_pyfile(_conf_file)

# Load Logger
logging.basicConfig(level=logging.INFO)
logging.info('Starting API Logger...')

# Load SQLAlchemy and Alembic
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

if app.config["API_ENABLED"]:
    import ranker.api
