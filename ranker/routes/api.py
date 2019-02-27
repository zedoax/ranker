from datetime import datetime

from ranker import app, db
from ranker.utils import ldap_get_member
from ranker.models import Player, Match


@app.route("/api/v1/new_match/<winner_uid>/<loser_uid>/", methods=["POST"])
def create_match(winner_uid, loser_uid):
    winner = Player.get_player(winner_uid)
    loser = Player.get_player(loser_uid)

    if winner is None:
        winner = new_player(winner_uid)
    if loser is None:
        loser = new_player(loser_uid)

    winner_rank = min(winner.rank, loser.rank)
    loser_rank = max(loser.rank, winner.rank)

    winner.rank = winner_rank
    loser.rank = loser_rank

    db.session.add(Match(date=datetime.now(), winner=winner, loser=loser))
    db.session.commit()
    return "Success: Match created"


def new_player(uid):
    member = ldap_get_member(uid)

    rank = Player.get_next_rank()
    player = Player(uid=uid, name=member.cn, rank=rank)

    db.session.add(player)

    db.session.commit()
    ranker = Player.get_player(uid)

    return ranker
