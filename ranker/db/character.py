from sqlalchemy import Column, String, ForeignKey

from ranker.db import db


class Character(db.Model):
    __tablename__ = "characters"
    name = Column(String(64), primary_key=True)
    game = Column(ForeignKey("games.id"), nullable=False)
    favicon = Column(String(256), nullable=False)
    img = Column(String(256), nullable=False)

    @classmethod
    def get_character(cls, name=None, game=None):
        if name:
            return cls.query.filter(cls.name == name)
        if game:
            return cls.query.filter(cls.game == game)
        return cls.query.all()
