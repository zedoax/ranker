from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from ranker.db import db


class Game(db.Model):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), unique=True, nullable=False)
    img = Column(String(256), nullable=False)
    description = Column(String(500), nullable=False)
    max_rounds = Column(Integer, nullable=False)
    min_rounds = Column(Integer, nullable=False)

    seasons = relationship("Season")

    @classmethod
    def get_game(cls, _id=None, title=None):
        if _id:
            return cls.query.filter(cls.id == _id).first()
        if title:
            return cls.query.filter(cls.title == title).first()
        return cls.query.all()
