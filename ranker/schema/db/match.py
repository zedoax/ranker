from marshmallow import fields

from ranker.schema.db.score import ScoreSchema
from ranker.schema.db.user import UserSchema
from .. import ma


class MatchSchema(ma.ModelSchema):
    id = fields.Integer()
    date = fields.Date()
    winner = fields.Nested(ScoreSchema(only=("user.username", "user.first_name", "user.last_name", "user.profile_img")))
    loser = fields.Nested(ScoreSchema(only=("user.username", "user.first_name", "user.last_name", "user.profile_img")))
    witness = fields.Nested(UserSchema(only=("first_name", "last_name",)))
    winner_wins = fields.Integer()
    loser_wins = fields.Integer()
    challenger_is_winner = fields.Boolean()
