from marshmallow import fields, validates, ValidationError

from ranker.db.user import User
from ranker.schema import ma


class Cancel(ma.ModelSchema):
    challenger = fields.String(required=True)
    challenged = fields.String(required=True)

    @validates('challenger')
    def validates_challenger(self, value):
        if not User.get_user(username=value):
            raise ValidationError('Your opponent is not a ranker player!')

    @validates('challenged')
    def validates_challenged(self, value):
        if not User.get_user(username=value):
            raise ValidationError('You are not a ranker player. Login to signup')
