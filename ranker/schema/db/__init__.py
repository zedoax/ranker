from .character import CharacterSchema
from .game import GameSchema
from .match import MatchSchema
from .score import ScoreSchema
from .season import SeasonSchema
from .user import UserSchema

character_schema = CharacterSchema()
characters_schema = CharacterSchema(many=True)
game_schema = GameSchema()
games_schema = GameSchema(many=True)
match_schema = MatchSchema()
matches_schema = MatchSchema(many=True)
score_schema = ScoreSchema()
scores_schema = ScoreSchema(many=True)
season_schema = SeasonSchema()
seasons_schema = SeasonSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
