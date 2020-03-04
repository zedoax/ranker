from marshmallow import fields

from . import ma


class Witness(ma.ModelSchema):
    winner = fields.String(required=True)
    loser = fields.String(required=True)
    winner_wins = fields.Integer(required=True)
    loser_wins = fields.Integer(required=True)
    witness = fields.String(required=True)


witness_schema = Witness()
