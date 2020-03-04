from marshmallow import fields

from . import ma


class Challenge(ma.ModelSchema):
    challenged = fields.String(required=True)
    season = fields.Integer(required=True)


challenge_schema = Challenge()
