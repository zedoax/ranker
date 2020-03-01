from marshmallow import fields

from . import ma


class UserSchema(ma.ModelSchema):
    username = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    slack_id = fields.String()
    twitch_id = fields.String()
    twitter_id = fields.String()
    profile_img = fields.String()
    witness = fields.Boolean()
    admin = fields.Boolean()
    scores = fields.List(fields.Nested("ScoreSchema", exclude=("user",)))


user_schema = UserSchema()
users_schema = UserSchema(many=True)
