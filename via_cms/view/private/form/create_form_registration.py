#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import Optional

from via_cms.model.internal.role_dao import Role
from via_cms.model.internal.user_dao import User
from via_cms.util.helper import get_locale


class CreateFormRegistration(FlaskForm):
    username = StringField(_l('User name <small>(required)</small>'), validators=[DataRequired(), Length(min=3, max=55)])
    alias_ar = StringField(_l('Alias in arabic <small>(required)</small>'), validators=[DataRequired(), Length(min=1, max=55)])
    alias_en = StringField(_l('Alias in english <small>(required)</small>'), validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField(_l('Email <small>(required)</small>'), validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField(_l('Password <small>(required)</small>'), validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField(_l('Verify password <small>(required)</small>'),
                            [DataRequired(), EqualTo('password', message=_l('Passwords must match'))])
    role_list = SelectField(_l('Role list (except admin)'), validators=[Optional()])


    def __init__(self, *args, **kwargs):
        super(CreateFormRegistration, self).__init__(*args, **kwargs)
        self.user = None
        lang = get_locale()
        if lang == 'ar':
            self.role_list.choices = [(role.name, role.label_ar) for role in Role.query if role.name != 'admin']
        elif lang == 'en':
            self.role_list.choices = [(role.name, role.label_en) for role in Role.query if role.name != 'admin']


    def validate(self):
        initial_validation = super(CreateFormRegistration, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append(_l("Username already registered"))
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append(_l("Email already registered"))
            return False
        return True


class EmailForm(FlaskForm):
    email = StringField(_l('Email <small>(required)</small>'), validators=[DataRequired(), Email()])


class PasswordForm(FlaskForm):
    password = PasswordField('Password <small>(required)</small>', validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password <small>(required)</small>'),
                              validators=[DataRequired(), EqualTo('password', message=_l('Passwords must match'))])


class UsernameForm(FlaskForm):
    username = StringField('Username <small>(required)</small>', validators=[DataRequired()])
    username2 = StringField('Confirm Username <small>(required)</small>',
                            validators=[DataRequired(), EqualTo('username', message=_l('Usernames must match'))])
