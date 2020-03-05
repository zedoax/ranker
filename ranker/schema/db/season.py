from marshmallow import fields

from .game import GameSchema
from .score import ScoreSchema
from .. import ma


class SeasonSchema(ma.ModelSchema):
    id = fields.Integer()
    name = fields.String()
    banner = fields.String()
    start = fields.Date()
    end = fields.Date()
    scores = fields.List(fields.Nested(ScoreSchema(exclude=("season",))))
    game = fields.Nested(GameSchema(exclude=("seasons",)))
