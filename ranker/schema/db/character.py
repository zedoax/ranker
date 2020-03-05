from ranker.db.character import Character
from .. import ma


class CharacterSchema(ma.ModelSchema):
    class Meta:
        model = Character
