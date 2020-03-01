from flask import url_for, jsonify, make_response, redirect, request, json
from requests import post
from slackeventsapi import SlackEventAdapter

from ranker import app
from ranker.api.utils import ldap_get_member_slack

slack_events = SlackEventAdapter(app.config['SLACK_API_KEY'], "/slack/events", app)


def create_match(args):
    """ Process match creation event """
    if len(args) != 2:
        return "Usage: /challenge @opponent", False
    if args[0] == args[1]:
        return "Sorry, you cannot challenge yourself", False
    if ldap_get_member_slack(args[0]) is None:
        return "Sorry, you do not have a valid slack id configured. " \
               "Please visit https://eac.csh.rit.edu/ to link", False
    if ldap_get_member_slack(args[1]) is None:
        return "Sorry, they do not have a valid slack id configured. " \
               "Please have them visit https://eac.csh.rit.edu/ to link", False
    if find_match(paired_matches, args[0]) is not None:
        return "Sorry, you currently have an ongoing match", False
    if find_match(unpaired_matches, args[0]) is not None:
        return "Sorry, you cannot issue multiple challenges.  " \
               "You must cancel your previous challenge before issuing another", False
    if find_match(paired_matches, args[1]) is not None:
        return "Sorry, they already have an ongoing match", False
    unpaired_matches.append(SlackMatch(args[0], args[1]))
    return "You have issued a challenge!", True


def accept_match(args):
    """ Process accept event """
    if len(args) != 2:
        return "Usage: /accept @challenger", False
    if args[0] == args[1]:
        return "Sorry, you cannot accept your own challenge"
    match = find_match(unpaired_matches, args[1])
    if match is None:
        return "You are not currently being challenged", False
    if match.contains_player(args[0]) is None:
        return "You are not currently being challenged", False
    match.accept()
    paired_matches.append(match)
    unpaired_matches.remove(match)
    return "You have accepted the challenge!", True


def cancel_match(args):
    """ Process cancel match event """
    if len(args) != 1:
        return "Usage: /cancel", False
    paired = False
    match = find_match(unpaired_matches, args[0])
    if match is None:
        match = find_match(paired_matches, args[0])
        paired = True

    if match is None:
        return "Could not find match to cancel", False
    if paired:
        paired_matches.remove(match)
    else:
        unpaired_matches.remove(match)

    return "You have cancelled your challenge", True


def remove_match(args):
    """ STUB """
    # STUB
    return False


# Valid Witness Required
def add_admin(args):
    """ Process add witness event """
    if len(args) != 2:
        return "Usage /add_witness @player", False
    if args[0] == args[1]:
        return "Sorry, those two names are the same", False
    admin = ldap_get_member_slack(args[0])
    new_witness = ldap_get_member_slack(args[1])
    if admin is None:
        return "Sorry, you do not have a valid slack id configured. " \
               "Please visit https://eac.csh.rit.edu/ to link", False
    if new_witness is None:
        return "Sorry, they do not have a valid slack id configured. " \
               "Please visit https://eac.csh.rit.edu/ to link", False
    if not Player.get_player(admin.uid).witness:
        return "Sorry, you are not a witness", False
    response = post("https://" + app.config['SERVER_NAME'] + url_for("create_witness"), json={
            'uid': new_witness.uid
        })

    if response.status_code != 200:
        return json.loads(response.text)['message'], False
    return "You have added a witness", True


def remove_admin(args):
    """ STUB """
    if len(args) != 1:
        return False
    return True


# Valid Witness Required
def witness_match(args):
    """ Process witness event """
    if len(args) != 4:
        return "Usage: /witness @winner winner_score loser_score", False
    witness = args[0]
    match = find_match(paired_matches, args[1])
    if match is None:
        return "That user has no matches which need a witness", False
    if not match.accepted:
        return "Match has not been accepted yet", False
    winner = match.get_player(args[1])
    loser = match.get_player()
    winner_score = int(args[2])
    loser_score = int(args[3])

    data, valid = csh_create_match(winner, loser, winner_score, loser_score, witness)

    if not valid:
        return "Sorry, " + data['error'] + \
               " has no or invalid slack id configured. Please visit https://eac.csh.rit.edu/ to link", False

    response = post("https://" + app.config['SERVER_NAME'] + url_for("create_match"), json=data)

    if response.status_code != 200:
        match.add_player(winner)
        match.add_player(loser)
        paired_matches.append(match)
        return json.loads(response.text)['message'], False
    paired_matches.remove(match)
    return "Match has been witnessed and recorded", True


def change_main(args):
    if len(args) < 2:
        return "Usage: /main main_name", False
    if ldap_get_member_slack(args[0]) is None:
        return "Sorry, you do not have a valid slack id configured. " \
               "Please visit https://eac.csh.rit.edu/ to link", False

    player = ldap_get_member_slack(args[0])
    name = " ".join(args[1:])

    response = post("https://" + app.config['SERVER_NAME'] + url_for("change_main"), json={
        'uid': player.uid,
        'name': name
    })
    if response.status_code != 200:
        return json.loads(response.text)['message'], False
    return "You are now a " + name + " main!", True


BOT_ACTION_FUNCTIONS = {
    '/accept': accept_match,
    '/challenge': create_match,
    '/cancel': cancel_match,
    '/add_witness': add_admin,
    '/retire': remove_admin,
    '/witness': witness_match,
    '/main': change_main
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


@app.route("/api/v1/slack/command", methods=["POST"])
def app_events_api():
    """ Process sent command """
    content = request.form.to_dict(flat=False)
    channel = content.get('channel_id', [])[0]
    user = str(content.get('user_id', [''])[0])
    command = str(content.get('command', [''])[0])
    args = []
    if len(content.get('text', [''])[0]) > 0:
        args = [slack_convert_players(item) for item in str(content['text'][0]).split(" ")]

    fn = BOT_ACTION_FUNCTIONS[command]
    args.insert(0, user)
    response, valid = fn(args)
    if valid:
        return jsonify({
                'response_type': 'in_channel',
                'text': response
            })
    return jsonify({
            'response_type': 'in_channel',
            'text': response
        })


def find_match(match_list, player):
    """ Locate the match belonging to a player from a list of matches """
    for match in match_list:
        if player in match.players:
            return match
    return None


def csh_create_match(winner, loser, winner_score, loser_score, witness):
    """ Create a Match object from given parameters """
    winner_profile = ldap_get_member_slack(winner)
    loser_profile = ldap_get_member_slack(loser)
    witness_profile = ldap_get_member_slack(witness)

    if winner_profile is None:
        return {'error': 'winner'}, False
    if loser_profile is None:
        return {'error': 'loser'}, False
    if witness_profile is None:
        return {'error': 'witness'}, False

    return {
        'winner_uid': winner_profile.uid,
        'loser_uid': loser_profile.uid,
        'witness_uid': witness_profile.uid,
        'winner_score': winner_score,
        'loser_score': loser_score
    }, True


def convert_slack_id(string):
    """ Extract SlackID from Slack user string """
    user_start = string.find('<')
    user_index = string.find('@')
    user_trans = string.find('|')
    user_end = string.find('>')
    if user_start == -1 or user_index == -1 or user_trans == -1 or user_end == -1:
        return string
    return string[:user_start] + string[user_index+1:user_trans] + string[user_end+1:]


@app.route("/slack/direct_install")
def direct_install():
    """ Process direct install requests """
    return redirect("""https://cshrit.slack.com/oauth/
    563574560288.c7032ad2a0c916712246aff79853365685a3f48bb445e0939d7675e6bddea57e?team=1""", 302)
