
"""Model unit tests."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#



import datetime as dt

import pytest

from via_cms.model.internal.user_dao import User
from via_cms.model.internal.role_dao import Role
from .factories import UserFactory


@pytest.mark.usefixtures('model')
class TestUser:

    def test_get_by_id(self):
        user = User('foo', 'foo@bar.com')
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        user = User(username='foo', email='foo@bar.com')
        user.save()
        assert bool(user.created)
        assert isinstance(user.created, dt.datetime)

    def test_password_is_nullable(self):
        user = User(username='foo', email='foo@bar.com')
        user.save()
        assert user.password is None

    def test_factory(self, db):
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created)
        # assert user.is_admin is False
        assert user.active is True
        assert user.check_password('myprecious')

    def test_check_password(self):
        user = User.create(username="foo", email="foo@bar.com",
                    password="foobarbaz123")
        assert user.check_password('foobarbaz123') is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_role_list(self):
        role = Role(name='private')
        role.save()
        u = UserFactory()
        u.role_list.append(role)
        u.save()
        assert role in u.role_list
