#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from flask import Blueprint
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.internal.user_dao import User
from via_cms.util.helper import flash_errors
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.view.private.form.create_form_registration import CreateFormRegistration
from via_cms.view.private.form.create_form_registration import PasswordForm
from via_cms.view.private.form.create_form_registration import UsernameForm

logger = LoggerManager.get_logger('manager_user')

bp = Blueprint("private.user.manager_user", __name__, url_prefix='/private/admin/user/management',
               static_folder="../static")


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        logger.info('Changing own password user_id: {}, user_name: {}'.format(current_user.id, current_user.username))
        current_user.set_password(form.password.data)
        current_user.save()
        return redirect(url_for('user.profile'))
    else:
        flash_errors(form)

    return render_extensions('user/change_password.html', resetform=form)


@bp.route('/change_username', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def change_username():
    form = UsernameForm()
    if form.validate_on_submit():
        logger.info('Changing own username user_id: {}, user_name: {}'.format(current_user.id, current_user.username))
        current_user.username = form.username.data
        current_user.save()
        return redirect(url_for('user.profile'))
    else:
        flash_errors(form)

    return render_extensions('user/change_username.html', resetform=form)


@bp.route("/register", methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def register():
    register_form = CreateFormRegistration(request.form, csrf_enabled=False)
    if register_form.validate_on_submit():
        logger.info('Registering new user ; user_name: {}'.format(register_form.username.data))

        new_user = User.create(username=register_form.username.data, first_name=register_form.first_name.data,
                               last_name=register_form.last_name.data, email=register_form.email.data,
                               password=register_form.password.data,
                               active=True)
        flash(_l("Thank you for registering. You can now log in."), _l('success'))
        return redirect(url_for('public.home'))
    else:
        flash_errors(register_form)
    return render_extensions('private/user/register.html', register_form=register_form)
