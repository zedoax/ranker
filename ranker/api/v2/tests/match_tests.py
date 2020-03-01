import unittest
from datetime import datetime, timedelta

from ranker import db, app
from ranker.api.v2.match import get_matches
from ranker.db import User, season, game, score, match


class TestDB(unittest.TestCase):
    def setUp(self):
        db.init_app(app)
        db.create_all()
        test_user = User(name='John Doe', admin=True, witness=True)
        test_game = game(id='ssbu', title='Super Smash Bros. Ultimate')
        test_season = season(start=datetime.now(), end=datetime.now() + timedelta(days=1), game=test_game)
        test_score_one = score(player=test_user, season=test_season)
        test_score_two = score(player=test_user, season=test_season)
        test_match = match(season=test_season, plus_score=10, minus_score=10,
                           winner=test_score_one, loser=test_score_two, witness=test_user)
        db.session.add(test_user)
        db.session.add(test_game)
        db.session.add(test_season)
        db.session.add(test_score_one)
        db.session.add(test_score_two)
        db.session.add(test_match)
        db.session.commit()

    def test_get_matches(self):
        matches = get_matches('Super Smash Bros.')
        assert matches is not None and matches.length > 0

    def tearDown(self):
        db.drop_all()
