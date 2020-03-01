from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ranker.db import db
from ranker.db.game import Game


class Season(db.Model):
    """ Season class """
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(25), nullable=False)
    banner = Column(String(256), nullable=False)
    game_id = Column(ForeignKey("games.id"), nullable=False)
    start = Column(DateTime, nullable=False, default=datetime.now())
    end = Column(DateTime, nullable=False)

    scores = relationship("Score", order_by="Score.score.desc()")
    game = relationship("Game", back_populates="seasons")

    @classmethod
    def get_season(cls, _id=None, game=None, username=None, name=None, date=None):
        if _id:
            return cls.query.filter(cls.id == _id).first()
        if name:
            return cls.query.filter(cls.name == name).first()
        if game:
            return cls.query.filter(cls.game_id == game).all()
        if username:
            return cls.query.filter(cls.scores.any(username=username)).all()
        if date:
            return cls.query.join(Game).filter(cls.start < date, cls.end > date).all()
        return cls.query.all()

    @classmethod
    def get_scores(cls, _id):
        return cls.query.filter(cls.id == _id).first().scores
