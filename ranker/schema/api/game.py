from marshmallow import fields
from marshmallow.validate import Length

from ranker.schema import ma


class Game(ma.ModelSchema):
    title = fields.String(required=True, validate=Length(max=50))
    img = fields.String(required=True, validate=Length(max=256))
    description = fields.String(required=True, validate=Length(max=500))
