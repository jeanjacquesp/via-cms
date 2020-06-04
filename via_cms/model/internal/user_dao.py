#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#

import datetime as dt

from flask_login import UserMixin
from sqlalchemy.orm import validates

from via_cms.extension import bcrypt
from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model.internal.role_dao import Role


class User(UserMixin, Model):
    __tablename__ = 'user_tbl'

    # flask packages required to name the identifier column: id, no other choice.
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    username = db.Column(db.Unicode(64), unique=True, nullable=False)
    email = db.Column(db.Unicode(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=dt.datetime.utcnow)
    alias_ar = db.Column(db.Unicode(64), nullable=True)
    alias_en = db.Column(db.Unicode(64), nullable=True)
    active = db.Column(db.Boolean, default=False)
    #
    post_list = db.relationship('FeedPost', backref=db.backref('editor'))
    basket_list = db.relationship('Basket', backref=db.backref('editor'))
    #
    role_list = db.relationship('Role', secondary='user_role_tbl', backref=db.backref('user_list_br', lazy='dynamic'))

    # TODO rights for accesses.

    def __init__(self, username, email, password=None, **kwargs):
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None


    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)


    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)


    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)


    @classmethod
    def get_by_id(cls, user_id):
        if any((isinstance(user_id, (str, bytes)) and user_id.isdigit(), isinstance(user_id, (int, float))), ):
            return cls.query.get(int(user_id))
        return None


    def get_geoloc_rights(self):
        result = []
        role_list = self.role_list
        for role in role_list:
            geoloc_list = role.geoloc_list
            for geoloc in geoloc_list:
                result.append(geoloc.id)
        return result


    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address


    def is_admin(self):
        return 'admin' in (x.principal for x in self.role_list)


    def is_supervisor(self):
        return 'supervisor' in (x.principal for x in self.role_list) or self.is_admin()


    def is_supervisor_news(self):
        return 'supervisor_news' in (x.principal for x in self.role_list) or self.is_supervisor() or self.is_admin()


    def is_supervisor_price(self):
        return 'supervisor_price' in (x.principal for x in self.role_list) or self.is_supervisor() or self.is_admin()


    def is_editor(self):
        return 'editor' in (x.principal for x in self.role_list) or self.is_supervisor() or self.is_admin()


    def is_editor_price(self):
        # A price editor is an editor limited to edit prices
        return 'editor/price' in (x.principal for x in
                                  self.role_list) or self.is_editor() or self.is_supervisor() or self.is_admin()


    def is_editor_news(self):
        # A price editor is an editor limited to edit news
        return 'editor/news' in (x.principal for x in
                                   self.role_list) or self.is_editor() or self.is_supervisor() or self.is_admin()


    def is_allowed(self, requirement_list):
        for role in self.role_list:
            if role.principal in requirement_list:
                return True
        return False


    @staticmethod
    def import_from_csv(file_path):
        import csv

        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
            first = True
            for row in reader:
                if first:
                    first = False
                else:
                    id = row[0]
                    username = row[1]
                    email = row[2]
                    password = row[3]
                    alias_ar = row[4]
                    alias_en = row[5]
                    role_id_columnseperated_list = row[6]
                    if role_id_columnseperated_list:
                        role_id_columnseperated_list = role_id_columnseperated_list.split(':')
                    user = User(id=int(id), username=username, email=email, password=password, alias_ar=alias_ar,
                                alias_en=alias_en, active=True)
                    for role_id in role_id_columnseperated_list:
                        role = Role.query.get(int(role_id))
                        user.role_list.append(role)
                    user.save()
