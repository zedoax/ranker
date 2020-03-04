import re

from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError

from . import ma


class Command(ma.ModelSchema):
    channel_id = fields.String(required=True)
    user_id = fields.String(required=True)
    command = fields.String(required=True)
    text = fields.String(required=True)

    @validates('user_id')
    def validate_user_id(self, value):
        slack_regex = re.compile('^U[A-Za-z0-9]{8}$')
        if not slack_regex.match(value):
            raise ValidationError('Invalid Regex')

    @validates('command')
    def validate_command(self, value):
        if value not in ['/challenge', '/accept', '/cancel', '/witness']:
            raise ValidationError('Invalid Command')


command_schema = Command()
