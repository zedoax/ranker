from marshmallow import fields

from . import ma


class GameSchema(ma.ModelSchema):
    id = fields.Integer()
    title = fields.String()
    img = fields.String()
    description = fields.String()
    seasons = fields.List(fields.Nested("SeasonSchema", exclude=("game",)))
    max_rounds = fields.Integer()
    min_rounds = fields.Integer()


game_schema = GameSchema()
games_schema = GameSchema(many=True)
