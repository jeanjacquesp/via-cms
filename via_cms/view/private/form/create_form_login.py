#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from flask import flash
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import Field
from wtforms import PasswordField
from wtforms import StringField
from wtforms.validators import DataRequired

from via_cms.model.internal.user_dao import User


class CreateFormLogin(FlaskForm):
    internal = Field('')
    username = StringField(_l('Username <small>(required)</small>'), validators=[DataRequired()])
    password = PasswordField(_l('Password <small>(required)</small>'), validators=[DataRequired()])


    def __init__(self, *args, **kwargs):
        super(CreateFormLogin, self).__init__(*args, **kwargs)
        self.user = None


    def validate(self):
        initial_validation = super(CreateFormLogin, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data.lower()).first()
        if not self.user or not self.user.check_password(self.password.data) or not self.user.active:
            flash(_l("Invalid username or password."), category="warning")
            return False

        return True
