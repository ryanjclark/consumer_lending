import pytest
import sys
sys.path.append("..")
import flask_app


def test_index():
    flask_app.app.testing = True
    client = flask_app.app.test_client()

    r = client.get('/')
    assert r.status_code == 200
