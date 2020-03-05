from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length

from ranker.schema import ma


class Season(ma.ModelSchema):
    name = fields.String(required=True, validate=Length(max=25))
    banner = fields.String(required=True, validate=Length(max=256))
    game = fields.Integer(required=True)
    start = fields.DateTime(required=True)
    end = fields.DateTime(required=True)

    @validates('start')
    def validate_start(self, value):
        if value >= self.end:
            raise ValidationError('Season cannot start after it ends')

    @validates('end')
    def validate_end(self, value):
        if value < self.end:
            raise ValidationError('Season cannot end before it starts')
