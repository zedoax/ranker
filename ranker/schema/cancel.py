from marshmallow import fields

from . import ma


class Cancel(ma.ModelSchema):
    challenger = fields.String(required=True)


cancel_schema = Cancel()
