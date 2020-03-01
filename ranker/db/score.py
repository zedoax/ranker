from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ranker.db import db


class Score(db.Model):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(ForeignKey("users.username"), nullable=False)
    season_id = Column(ForeignKey("seasons.id"), nullable=False)
    score = Column(Integer, nullable=False, default=100)
    main_name = Column(ForeignKey("characters.name"), nullable=True)

    user = relationship("User", back_populates="scores")
    season = relationship("Season", back_populates="scores")
    main = relationship("Character")

    @classmethod
    def get_score(cls, _id=None, username=None, season=None):
        if _id:
            return cls.query.filter(cls.id == _id).first()
        if username and season:
            return cls.query.filter(cls.username == username, cls.season_id == season).first()
        if username:
            return cls.query.filter(cls.username == username).all()
        if season:
            return cls.query.filter(cls.season_id == season).all()
        return cls.query.all()
