from flask import Blueprint

from ranker.db import scores
from ranker.schema.db import scores_schema, score_schema

score_bp = Blueprint("scores", __name__, url_prefix="/scores")


@score_bp.route("", methods=["GET"])
def get_scores():
    _scores = scores.get_score()
    return scores_schema.dumps(_scores)


@score_bp.route("/<int:_id>", methods=["GET"])
def get_score_by_id(_id):
    _scores = scores.get_score(_id=_id)
    return scores_schema.dumps(_scores)


@score_bp.route("/<int:season>/<string:username>", methods=["GET"])
def get_score(season, username):
    score = scores.get_score(username=username, season=season)
    if not score:
        return None
    return score_schema(score)
