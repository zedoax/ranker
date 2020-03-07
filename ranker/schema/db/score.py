from marshmallow import fields

from .user import UserSchema
from .character import CharacterSchema
from .. import ma


class ScoreSchema(ma.ModelSchema):
    id = fields.Integer()
    username = fields.String()
    score = fields.Integer()
    season = fields.Nested("SeasonSchema", exclude=("scores",))
    user = fields.Nested(UserSchema(only=("username", "first_name", "last_name", "profile_img",)))
    main = fields.Nested(CharacterSchema)
