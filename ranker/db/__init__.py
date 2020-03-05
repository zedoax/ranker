from ranker import db as ranker_db
from ranker import migrate as ranker_migrate

db = ranker_db
migrate = ranker_migrate

from .game import Game
from .match import Match
from .score import Score
from .season import Season
from .user import User

games = Game
matches = Match
scores = Score
seasons = Season
users = User
