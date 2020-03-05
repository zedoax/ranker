from marshmallow import fields, validates, ValidationError

from ranker.db.user import User
from .. import ma


class Command(ma.ModelSchema):
    channel_id = fields.String(required=True)
    user_id = fields.String(required=True)
    command = fields.String(required=True)
    text = fields.String(required=True)

    @validates('user_id')
    def validate_user_id(self, value):
        if not User.get_user(slack_id=value):
            raise ValidationError('Your Slack ID is not linked to a Ranker player. Use eac to link')

    @validates('command')
    def validate_command(self, value):
        if value not in ['/challenge', '/accept', '/cancel', '/witness']:
            raise ValidationError('Invalid Command')
