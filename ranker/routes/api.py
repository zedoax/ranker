from datetime import datetime

from flask import request, make_response
from flask.json import jsonify
from sqlalchemy.exc import SQLAlchemyError

from ranker import app, db
from ranker.utils import ldap_get_member
from ranker.models import Player, Match, Main

RATING_IMPACT_CONSTANT = app.config['RATING_IMPACT_CONSTANT']
RATING_DEFAULT = app.config['RATING_DEFAULT']


@app.route("/api/v1/new_match/", methods=["POST"])
def create_match():
    # If the request isn't in json format: error out
    if not request.is_json:
        return make_response(jsonify(message="Error: Format incorrect"), 400)
    content = request.get_json()

    # If the json does not contain the correct values: error out
    if 'winner_uid' not in content and 'loser_uid' not in content \
            and 'winner_score' not in content and 'loser_score' not in content \
            and 'witness' not in content:
        return make_response(jsonify(message="Error: Invalid Request"), 400)

    # Pull all values
    winner_uid = content['winner_uid']
    loser_uid = content['loser_uid']
    winner_score = int(content['winner_score'])
    loser_score = int(content['loser_score'])
    witness_uid = content['witness_uid']

    # Verify the challenge rounds are legal
    if winner_score + loser_score > app.config['MATCH_ROUNDS']:
        return make_response(jsonify(message="Sorry, that match had too many rounds"), 400)
    if winner_score < int(int(app.config['MATCH_ROUNDS']) / 2) + 1:
        return make_response(jsonify(message="Sorry, the winner's score is invalid"), 400)
    if winner_score < loser_score:
        return make_response(jsonify(message="Umm, the winner's score is lower than the losers!"), 400)

    # Retrieve the players
    winner = Player.get_player(winner_uid)
    loser = Player.get_player(loser_uid)
    witness = Player.get_player(witness_uid)

    # Create players if they don't already exist
    if winner is None:
        winner = new_player(winner_uid)
    if loser is None:
        loser = new_player(loser_uid)
    if witness is None:
        witness = new_player(witness_uid)

    # Verify the witness is legitimate
    if not witness.witness:
        return make_response(jsonify(message="Sorry, that player is not a witness"), 400)

    # Calculate Rating Changes
    rating_winner = pow(10, (winner.rating / 400))
    rating_loser = pow(10, (loser.rating / 400))

    expected_rating_winner = rating_winner / (rating_winner + rating_loser)
    expected_rating_loser = rating_loser / (rating_winner + rating_loser)

    winner.rating = winner.rating + RATING_IMPACT_CONSTANT * (1 - expected_rating_winner)
    loser.rating = loser.rating + RATING_IMPACT_CONSTANT * (0 - expected_rating_loser)

    # Create the match, if fails: error out
    try:
        match = Match(date=datetime.now(), winner=winner, loser=loser,
                      winner_score=winner_score, loser_score=loser_score,
                      witness=witness)
        db.session.add(match)
        db.session.commit()
    except SQLAlchemyError:
        return make_response(jsonify(message="Error: DB insertion failed"), 500)

    return make_response(jsonify(message="Match has been successfully witnessed and recorded"), 200)


@app.route("/api/v1/add_main/", methods=["POST"])
def create_main():
    # If the request isn't in json format: error out
    if not request.is_json:
        return make_response(jsonify(message="Error: Format incorrect"), 400)
    content = request.get_json()

    # If the json does not contain the correct values: error out
    if 'name' not in content:
        return make_response(jsonify(message="Error: Invalid Request"), 400)
    name = content['name']
    main = Main(name=name)

    # Try to insert into database
    try:
        db.session.add(main)
        db.session.commit()
    except SQLAlchemyError:
        return make_response(jsonify(message="Error: DB insertion failed"), 500)

    return make_response(jsonify(message="Success: Main created"), 200)


@app.route("/api/v1/change_main/", methods=["POST"])
def change_main():
    # If the request isn't in json format: error out
    if not request.is_json:
        return make_response(jsonify(message="Error: Format incorrect"), 400)
    content = request.get_json()

    # If the json does not contain the correct values: error out
    if 'uid' not in content and 'name' not in content:
        return make_response(jsonify(message="Error: Invalid Request"), 400)

    # If the get, alter, or commit fails: error out
    try:
        # Get the correct objects
        player = Player.get_player(content['uid'])
        main = Main.get_main(content['name'])

        # Alter main
        player.main = main

        # Commit to db
        db.session.commit()
    except SQLAlchemyError:
        return make_response(jsonify(message="Error: DB alteration failed"), 500)

    return make_response(jsonify(message="Success: Main changed"), 200)


@app.route("/api/v1/new_witness/", methods=['POST'])
def create_witness():
    # If the request isn't in json format: error out
    if not request.is_json:
        return make_response(jsonify(message="Error: Format incorrect"), 400)
    content = request.get_json()

    # If the json does not contain the correct values: error out
    if 'uid' not in content:
        return make_response(jsonify(message="Error: Invalid Request"), 400)

    # If the insert or alteration fails: error out
    try:
        player = Player.get_player(content['uid'])

        if player is None:
            new_player(content['uid'])

        player.witness = True

        db.session.commit()
    except SQLAlchemyError:
        return make_response(jsonify(message="Error: DB alteration failed"), 500)

    return make_response(jsonify(message="Success: Witness added"), 200)


def new_player(uid):
    # Get member from ldap
    member = ldap_get_member(uid)

    player = Player(uid=uid, name=member.cn, rating=RATING_DEFAULT, joined=datetime.now())

    # Try to insert into the database
    try:
        db.session.add(player)
        db.session.commit()
    except SQLAlchemyError:
        return make_response(jsonify(message="Error: DB insertion failed"), 500)

    # Get the ranker
    return player
