from datetime import datetime

from sqlalchemy import Column, Integer, or_, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from ranker.db import db


class Match(db.Model):
    """ Match class """
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.now(), nullable=False)
    winner_id = Column(ForeignKey("scores.id"), nullable=False)
    loser_id = Column(ForeignKey("scores.id"), nullable=False)
    season_id = Column(ForeignKey("seasons.id"), nullable=False)
    winner_wins = Column(Integer, nullable=False)
    loser_wins = Column(Integer, nullable=False)
    winner_prev_score = Column(Integer, nullable=False)
    loser_prev_score = Column(Integer, nullable=False)
    challenger_is_winner = Column(Boolean, nullable=False)
    witness_username = Column(ForeignKey("users.username"), nullable=False)

    season = relationship("Season")
    winner = relationship("Score", foreign_keys=[winner_id])
    loser = relationship("Score", foreign_keys=[loser_id])
    witness = relationship("User")

    @classmethod
    def get_match(cls, _id=None, username=None, season=None, witness=None):
        if _id:
            return cls.query.filter(cls.id == _id).first()
        if username:
            return cls.query.filter(or_(cls.winner_username == username, cls.loser_username == username)).all()
        if season:
            return cls.query.filter(cls.season_id == season).all()
        if witness:
            return cls.query.filter(cls.witness_username == witness).all()
        return cls.query.all()
