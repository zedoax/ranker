from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from ranker.db import db


class User(db.Model):
    __tablename__ = "users"
    username = Column(String(64), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    slack_id = Column(String(10), nullable=True)
    twitch_id = Column(String(100), nullable=True)
    twitter_id = Column(String(15), nullable=True)
    profile_img = Column(String(256), nullable=False)
    witness = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)

    scores = relationship("Score")

    @classmethod
    def get_user(cls, username=None, slack_id=None, witness=False):
        if username:
            return cls.query.filter(cls.username == username).first()
        if slack_id:
            return cls.query.filter(cls.slack_id == slack_id).first()
        if witness:
            return cls.query.filter(witness).all()
        return cls.query.all()
