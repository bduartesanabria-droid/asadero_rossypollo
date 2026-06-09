import pytest
from datetime import datetime
from app.models import User, Match, Prediction


def test_user_password_hashing():
    user = User(username='user1', email='user1@example.com')
    user.set_password('secret')
    assert user.password_hash != 'secret'
    assert user.check_password('secret')
    assert not user.check_password('wrong')


def test_prediction_scoring_exact():
    match = Match(home_team='A', away_team='B', home_score=2, away_score=1, match_date='2026-01-01 00:00:00')
    pred = Prediction(predicted_home_score=2, predicted_away_score=1, match=match)
    assert pred.calculate_points() == 3


def test_prediction_scoring_same_outcome_draw():
    match = Match(home_team='A', away_team='B', home_score=1, away_score=1, match_date='2026-01-01 00:00:00')
    pred = Prediction(predicted_home_score=2, predicted_away_score=2, match=match)
    assert pred.calculate_points() == 1


def test_prediction_scoring_wrong_outcome():
    match = Match(home_team='A', away_team='B', home_score=3, away_score=2, match_date='2026-01-01 00:00:00')
    pred = Prediction(predicted_home_score=1, predicted_away_score=2, match=match)
    assert pred.calculate_points() == 0


@pytest.mark.usefixtures('app')
def test_unique_user_match_constraint(app):
    from app.models import db

    user = User(username='uniqueuser', email='unique@example.com')
    user.set_password('password')
    match = Match(home_team='A', away_team='B', match_date=datetime(2026, 1, 1, 0, 0))
    db.session.add_all([user, match])
    db.session.commit()

    prediction1 = Prediction(user_id=user.id, match_id=match.id, predicted_home_score=1, predicted_away_score=1)
    db.session.add(prediction1)
    db.session.commit()

    prediction2 = Prediction(user_id=user.id, match_id=match.id, predicted_home_score=2, predicted_away_score=2)
    db.session.add(prediction2)

    with pytest.raises(Exception):
        db.session.commit()
