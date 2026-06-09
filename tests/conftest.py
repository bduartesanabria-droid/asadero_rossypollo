import os
import tempfile

import pytest
from app import create_app
from app.models import db

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

def pytest_configure():
    # Force Flask to use the in-memory test database
    os.environ['FLASK_ENV'] = 'development'


@pytest.fixture(scope='session')
def app():
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()
