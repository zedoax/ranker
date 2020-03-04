from marshmallow import fields

from . import ma


class Accept(ma.ModelSchema):
    challenger = fields.String(required=True)


accept_schema = Accept()
