import json

from flask import url_for, jsonify, make_response, redirect, Blueprint
from requests import post
from slackeventsapi import SlackEventAdapter

from ranker import app, logging
from ranker.api.utils import get_request_form
from ranker.auth.oidc import OidcAuth
from ranker.db.season import Season
from ranker.db.user import User
from ranker.slack.utils import strip_id, rotate_token

slack_events = SlackEventAdapter(app.config['SLACK_API_KEY'], "/slack/events", app)

config = app.config
host_uri = "http://" + app.config["SERVER_NAME"]
slack_bp = Blueprint("slack", __name__, url_prefix="/slack")


def new_match(args):
    """ Process match create event """
    if len(args) != 3:
        return {"message": "Usage: /challenge @opponent"}

    challenger = User.get_user(slack_id=args[0])
    challenged = User.get_user(slack_id=args[1])
    if challenger is None:
        return {"message": "You have not yet logged into ranker, or have not yet linked slack to eac"}
    if challenged is None:
        return {"message": "Your opponent has not yet logged into ranker, or have not yet linked slack to eac"}

    data = {
        "user": challenger.username,
        "challenged": challenged.username,
        "season": args[2]
    }
    token = rotate_token()
    response = post(host_uri + url_for("matches.new_match"), json=data, auth=OidcAuth(token))
    logging.info(response)
    logging.info(data)
    return json.loads(response.content)


def accept_match(args):
    """ Process match accept event """
    if len(args) != 2:
        return {"message": "Usage: /accept @opponent"}

    challenged = User.get_user(slack_id=args[0])
    challenger = User.get_user(slack_id=args[1])
    if challenged is None:
        return {"message": "You have not yet logged into ranker, or have not yet linked slack to eac"}
    if challenger is None:
        return {"message": "Your opponent has not yet logged into ranker, or have not yet linked slack to eac"}

    data = {
        "user": challenged.username,
        "challenger": challenger.username
    }
    token = rotate_token()
    response = post(host_uri + url_for("matches.accept_match"), json=data, auth=OidcAuth(token))

    return json.loads(response.content)


def cancel_match(args):
    """ Process match cancel event """
    if len(args) != 2:
        return {"message": "Usage: /challenge @opponent"}

    challenged = User.get_user(slack_id=args[0])
    challenger = User.get_user(slack_id=args[1])
    if challenged is None:
        return {"message": "Your opponent's slack id is not linked to a ranker player!"}
    if challenger is None:
        return {"message": "Your slack id is not linked to a ranker player!"}

    data = {
        "user": challenged.username,
        "challenger": challenger.username
    }
    token = rotate_token()
    response = post(host_uri + url_for("matches.cancel_match"), json=data, auth=OidcAuth(token))

    return json.loads(response.content)


def witness_match(args):
    """ Process witness event """
    if len(args) != 5:
        return {"message": "Usage: /witness @winner @loser winner_wins loser_wins"}

    witness = User.get_user(slack_id=args[0])
    winner = User.get_user(slack_id=args[1])
    loser = User.get_user(slack_id=args[2])
    if witness is None:
        return {"message": "You have not yet logged into ranker, or have not yet linked slack to eac"}
    if winner is None:
        return {"message": "That winner has not yet logged into ranker, or have not yet linked slack to eac"}
    if loser is None:
        return {"message": "That loser has not yet logged into ranker, or have not yet linked slack to eac"}

    winner_wins = int(args[3])
    loser_wins = int(args[4])

    data = {
        "user": witness.username,
        "winner": winner.username,
        "loser": loser.username,
        "winner_wins": winner_wins,
        "loser_wins": loser_wins,
        "witness": witness.username
    }
    token = rotate_token()
    response = post(host_uri + url_for("matches.witness_match"), json=data, auth=OidcAuth(token))

    return json.loads(response.content)


BOT_ACTION_FUNCTIONS = {
    '/challenge': new_match,
    '/accept': accept_match,
    '/cancel': cancel_match,
    '/witness': witness_match
}


"""
@slack_events.on("app_mention")
def app_mention(event_data):
    args = event_data['text'].split(" ")
    fn = BOT_ACTION_FUNCTIONS[args[1]]
    args = args[2:]
    user = event_data['user']
    fn({
        'user': user.uid,
        'channel': event_data['channel'],
        'args': args
    })
"""


@slack_events.on("url_verification")
def app_verification(event_data):
    """ Verification event """
    return make_response(jsonify({
        'challenge': event_data['challenge']
    }), 200)


@slack_bp.route("/command/<int:game>", methods=["POST"])
def bot_command_game(game):
    """ Process sent command """
    seasons = Season.get_season(game=game)
    if not len(seasons) > 0:
        return jsonify({
            'response_type': 'in_channel',
            'text': "There are no active seasons for this game"
        })
    latest_season = seasons[0]
    content = get_request_form("channel_id", "user_id", "command", "text")
    args = []
    if len(content.get("text")) > 0:
        args = [strip_id(item) for item in content['text'].split(" ")]

    fn = BOT_ACTION_FUNCTIONS[content["command"]]
    args.insert(0, content.get("user_id"))
    args.append(latest_season.id)
    response = fn(args)
    return jsonify({
        'response_type': 'in_channel',
        'text': response.get("message")
    })


@slack_bp.route("/command", methods=["POST"])
def bot_command():
    """ Process sent command """
    content = get_request_form("channel_id", "user_id", "command", "text")
    args = []
    if len(content.get("text")) > 0:
        args = [strip_id(item) for item in content['text'].split(" ")]

    fn = BOT_ACTION_FUNCTIONS[content["command"]]
    args.insert(0, content.get("user_id"))
    response = fn(args)
    return jsonify({
        'response_type': 'in_channel',
        'text': response.get("message")
    })


@slack_bp.route("/direct_install")
def direct_install():
    """ Process direct install requests """
    return redirect("""https://cshrit.slack.com/oauth/
    563574560288.c7032ad2a0c916712246aff79853365685a3f48bb445e0939d7675e6bddea57e?team=1""", 302)
