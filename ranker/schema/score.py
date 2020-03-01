from marshmallow import fields

from ranker.schema.user import UserSchema
from . import ma
from .character import CharacterSchema


class ScoreSchema(ma.ModelSchema):
    id = fields.Integer()
    username = fields.String()
    score = fields.Integer()
    season = fields.Nested("SeasonSchema", exclude=("scores",))
    user = fields.Nested(UserSchema(only=("username", "first_name", "last_name", "profile_img",)))
    main = fields.Nested(CharacterSchema)


score_schema = ScoreSchema()
scores_schema = ScoreSchema(many=True)
