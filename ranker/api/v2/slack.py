from itertools import chain

from flask import url_for, jsonify, redirect, Blueprint
from marshmallow.exceptions import ValidationError
from requests import post
from slackeventsapi import SlackEventAdapter

from ranker import app
from ranker.api.utils import get_request_form
from ranker.auth.oidc import OidcAuth
from ranker.db.season import Season
from ranker.db.user import User
from ranker.schema.slack import command_schema
from ranker.slack.utils import strip_id, rotate_token, make_response

slack_events = SlackEventAdapter(app.config['SLACK_API_KEY'], "/slack/events", app)

host_uri = ("https://" if app.config["SSL_ENABLED"] else "http://") + app.config["SERVER_NAME"]
slack_bp = Blueprint("slack", __name__, url_prefix="/slack")


def new_match(args):
    if len(args) != 3:
        return "Usage: /challenge @opponent"

    challenger = User.get_user(slack_id=args[0])
    challenged = User.get_user(slack_id=args[1])
    season = Season.get_season(_id=args[2])

    if challenger is None:
        return "You have not yet logged into ranker, or have not yet linked slack to eac"
    if challenged is None:
        return "Your opponent has not yet logged into ranker, or have not yet linked slack to eac"

    data = {
        "challenger": challenger.username,
        "challenged": challenged.username,
        "season": season.id
    }

    token = rotate_token()
    response = post(host_uri + url_for('matches.new_match'), json=data, auth=OidcAuth(token, challenger.username))
    return response.text


def accept_match(args):
    if len(args) != 2:
        return "Usage: /accept @opponent"

    challenged = User.get_user(slack_id=args[0])
    challenger = User.get_user(slack_id=args[1])

    if challenged is None:
        return "You have not yet logged into ranker, or have not yet linked slack to eac"
    if challenger is None:
        return "Your opponent has not yet logged into ranker, or have not yet linked slack to eac"

    data = {
        "challenged": challenged.username,
        "challenger": challenger.username
    }

    token = rotate_token()
    response = post(host_uri+url_for('matches.accept_match'), json=data, auth=OidcAuth(token, challenged.username))
    return response.text


def cancel_match(args):
    if len(args) != 2:
        return "Usage: /cancel @opponent"

    challenged = User.get_user(slack_id=args[0])
    challenger = User.get_user(slack_id=args[1])

    if challenged is None:
        return "Your opponent's slack id is not linked to a ranker player!"
    if challenger is None:
        return "Your slack id is not linked to a ranker player!"

    data = {
        "challenged": challenged.username,
        "challenger": challenger.username
    }

    token = rotate_token()
    response = post(host_uri+url_for('matches.cancel_match'), json=data, auth=OidcAuth(token, challenged.username))
    return response.text


def witness_match(args):
    if len(args) != 5:
        return 'Usage: /witness @winner @loser winner_wins loser_wins'

    witness = User.get_user(slack_id=args[0])
    winner = User.get_user(slack_id=args[1])
    loser = User.get_user(slack_id=args[2])
    winner_wins = int(args[3])
    loser_wins = int(args[4])

    if witness is None:
        return 'You have not yet logged into ranker, or have not yet linked slack to eac'
    if winner is None:
        return 'That winner has not yet logged into ranker, or have not yet linked slack to eac'
    if loser is None:
        return 'That loser has not yet logged into ranker, or have not yet linked slack to eac'

    data = {
        "username": witness.username,
        "winner": winner.username,
        "loser": loser.username,
        "winner_wins": winner_wins,
        "loser_wins": loser_wins,
        "witness": witness.username
    }

    token = rotate_token()
    response = post(host_uri + url_for("matches.witness_match"), json=data, auth=OidcAuth(token, witness.username))
    return response.content


BOT_ACTION_FUNCTIONS = {
    '/challenge': new_match,
    '/accept': accept_match,
    '/cancel': cancel_match,
    '/witness': witness_match
}


@slack_events.on("url_verification")
def app_verification(event_data):
    return jsonify({'challenge': event_data['challenge']})


@slack_bp.route("/command", methods=["POST"])
def bot_command(season=None):
    try:
        content = get_request_form(command_schema)
    except ValidationError as error:
        return make_response(error)
    args = list(chain([content['user_id']], [strip_id(i) for i in content['text'].split()], [season] if season else []))

    command = BOT_ACTION_FUNCTIONS[content["command"]]
    response = command(args)
    return make_response(response)


@slack_bp.route("/command/<int:game>", methods=["POST"])
def bot_command_game(game):
    season = Season.current_season(game=game)
    if not season:
        return make_response('There are no active seasons for this game')
    return bot_command(season.id)


@slack_bp.route("/direct_install")
def direct_install():
    """ Process direct install requests """
    return redirect("""
    https://cshrit.slack.com/oauth/563574560288.c7032ad2a0c916712246aff79853365685a3f48bb445e0939d7675e6bddea57e?team=1
    """, 302)
