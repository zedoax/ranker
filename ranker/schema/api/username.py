from marshmallow import fields
from marshmallow.validate import Length

from ranker.schema import ma


class Username(ma.ModelSchema):
    username = fields.String(required=True, validate=Length(64))
