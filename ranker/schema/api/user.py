from marshmallow import fields
from marshmallow.validate import Length

from ranker.schema import ma


class User(ma.ModelSchema):
    username = fields.String(required=True, validate=Length(64))
    first_name = fields.String(required=True, validate=Length(50))
    last_name = fields.String(required=True, validate=Length(50))
    profile_img = fields.String(required=True, validate=Length(256))
