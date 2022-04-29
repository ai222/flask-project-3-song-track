from main import app, parseCSV, db, User
import pathlib

import os
from flask import session
import pytest


def client(app):
    return app.test_client()


def test_dashboardwithdennyacces():
    response = app.test_client().get('/')

    assert response.status_code == 302


def test_signup():
    response = app.test_client().get('/signup')

    assert response.status_code == 200


def test_signin():
    response = app.test_client().get('/signin')

    assert response.status_code == 200


def testfileuploadandprocessed():
    PARENT_PATH = str(pathlib.Path(__file__).parent.resolve())
    UPLOAD_FOLDER = 'bebu.csv'
    check = parseCSV(UPLOAD_FOLDER)
    num = 1
    if check:
        num = 0
    assert num == 1


def check_user():
    entry = User(username='testing', email='testingpytest@gmail.com', filename=None, password='password',
                 repassword='password')
    db.session.add(entry)
    db.session.commit()

    check = User.query.filter_by(username='testing').first()
    if check:
        assert True


def login(client):
    """Login helper function"""
    return client.post(
        "/signin",
        data=dict(username='testuser', password='testing'),
        follow_redirects=True
    )
