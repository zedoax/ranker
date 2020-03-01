from marshmallow import fields

from . import ma
from .score import ScoreSchema
from .game import GameSchema


class SeasonSchema(ma.ModelSchema):
    id = fields.Integer()
    name = fields.String()
    banner = fields.String()
    start = fields.Date()
    end = fields.Date()
    scores = fields.List(fields.Nested(ScoreSchema(exclude=("season",))))
    game = fields.Nested(GameSchema(exclude=("seasons",)))


season_schema = SeasonSchema()
seasons_schema = SeasonSchema(many=True)
