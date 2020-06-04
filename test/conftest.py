
"""Defines fixtures available to all tests."""

#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#



import pytest
from webtest import TestApp

from via_cms.config_flask import ConfigQaTesting
from via_cms.main import create_app
from via_cms.model._database import db as _db

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    _app = create_app(ConfigQaTesting)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture
def user(db):
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user
