from marshmallow import fields
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError

from ranker.db import users, seasons
from ranker.schema import ma


class Challenge(ma.ModelSchema):
    challenger = fields.String(required=True)
    challenged = fields.String(required=True)
    season = fields.Integer(required=True)

    @validates('challenger')
    def validate_challenger(self, value):
        if not users.get_user(username=value):
            raise ValidationError('You are not a ranker user')

    @validates('challenged')
    def validate_challenged(self, value):
        if not users.get_user(username=value):
            raise ValidationError('Your opponent is not a ranker user')

    @validates('season')
    def validate_season(self, value):
        if not seasons.get_season(value):
            raise ValidationError('That is not a valid season')
