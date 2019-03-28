from flask import render_template, redirect, url_for
from ranker import auth

from ranker import app
from ranker.models import Player, Match


@app.route("/")
@auth.oidc_auth("default")
def index():
    return redirect(url_for("ranking"), 302)


@app.route("/ranks/")
@auth.oidc_auth("default")
def ranking():
    ranked_players = Player.get_players_ranked()

    def sort_rank(player):
        return player.rank
    ranked_players.sort(key=sort_rank)

    return render_template("index.html", app=app, ranked_players=ranked_players)


@app.route("/player/<uid>/")
@auth.oidc_auth("default")
def ranker(uid):
    player = Player.get_player(uid)
    player_matches = Match.get_matches(player.uid)

    return render_template("ranker.html", app=app, ranked_player=player, ranked_matches=player_matches)


@app.route("/matches/")
@auth.oidc_auth("default")
def matches():
    ranked_matches = Match.get_all_matches()

    return render_template("matches.html", app=app, ranked_matches=ranked_matches)


@app.route("/match/<mid>/")
@auth.oidc_auth("default")
def match(mid):
    return ""


@app.route("/logout/")
@auth.oidc_logout
def logout():
    return redirect("http://csh.rit.edu")
