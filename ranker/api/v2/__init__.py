import ranker.api.v2.character
from ranker import app
from ranker.api.v2.game import game_bp
from ranker.api.v2.match import match_bp
from ranker.api.v2.score import score_bp
from ranker.api.v2.season import season_bp
from ranker.api.v2.user import user_bp
from ranker.api.v2.witness import witness_bp

app.register_blueprint(match_bp)
app.register_blueprint(game_bp)
app.register_blueprint(user_bp)
app.register_blueprint(season_bp)
app.register_blueprint(score_bp)
app.register_blueprint(witness_bp)
