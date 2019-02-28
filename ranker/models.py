from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, desc, or_, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import count

from ranker import db


class Player(db.Model):
    __tablename__ = "player"
    uid = Column(String(10), primary_key=True)
    name = Column(String(64), nullable=False)

    rank = Column(Integer, nullable=False)
    witness = Column(Boolean, default=False)

    # A ranked player can only have one main for now
    main_name = Column(String(20), ForeignKey("main.name"), nullable=True)
    main = relationship("Main", back_populates="players")

    @classmethod
    def get_next_rank(cls):
        return db.session.query(count(Player.rank)).scalar() + 1

    @classmethod
    def get_players_ranked(cls):
        return cls.query.order_by(desc(cls.rank)).all()

    @classmethod
    def get_player(cls, uid):
        return cls.query.filter_by(uid=uid).first()


class Main(db.Model):
    __tablename__ = "main"
    name = Column(String(32), primary_key=True)

    # A main can have many ranked players using it
    players = relationship("Player")

    @classmethod
    def get_players(cls, name):
        return cls.query.filter_by(name=name).first().players

    @classmethod
    def get_main(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def exists(cls, name):
        return len(cls.query.filter_by(name=name)) > 0


class Match(db.Model):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now(), nullable=False)

    # Each match has a winner and a loser
    winner_uid = Column(String(10), ForeignKey("player.uid"))
    loser_uid = Column(String(10), ForeignKey("player.uid"))
    witness_uid = Column(String(10), ForeignKey("player.uid"))

    winner = relationship("Player", foreign_keys=[winner_uid])
    loser = relationship("Player", foreign_keys=[loser_uid])
    witness = relationship("Player", foreign_keys=[witness_uid], uselist=False)

    # Each match has a total score
    winner_score = Column(Integer, nullable=False)
    loser_score = Column(Integer, nullable=True)

    @classmethod
    def get_all_matches(cls):
        return cls.query.order_by(desc(cls.date)).all()

    @classmethod
    def get_matches(cls, uid):
        return cls.query.filter(or_(cls.winner_uid == uid, cls.loser_uid == uid)).all()



