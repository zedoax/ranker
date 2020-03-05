from marshmallow import fields, validates, ValidationError

from ranker.db.user import User
from ranker.schema import ma


class Witness(ma.ModelSchema):
    winner = fields.String(required=True)
    loser = fields.String(required=True)
    winner_wins = fields.Integer(required=True)
    loser_wins = fields.Integer(required=True)
    witness = fields.String(required=True)

    @validates('winner')
    def validate_challenger(self, value):
        if not User.get_user(username=value):
            raise ValidationError('You are not a ranker user')

    @validates('loser')
    def validate_challenged(self, value):
        if not User.get_user(username=value):
            raise ValidationError('Your opponent is not a ranker user')

    @validates('witness')
    def validate_challenged(self, value):
        if not User.get_user(username=value):
            raise ValidationError('Your opponent is not a ranker user')
