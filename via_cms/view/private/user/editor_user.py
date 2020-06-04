#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import traceback

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_babel import lazy_gettext as _l
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.internal.role_dao import Role
from via_cms.model.internal.user_dao import User
from via_cms.util.helper import flash_errors
from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.view.private.form.create_form_registration import CreateFormRegistration
from via_cms.viewmodel.vm_user import itemize_user

logger = LoggerManager.get_logger('editor_user')

bp = Blueprint("private.user.editor_user", __name__, url_prefix='/private/admin/edition', static_folder="../static")


@bp.route('/user/<user_id>', methods=['GET'])
@login_required
@role_required(['admin'])
def editor_user(user_id: str):
    item = None
    try:
        id = int(user_id)
        item = itemize_user(id)
    except ValueError as e:
        logger.warning(traceback.print_exc())  # TODO exception

    return render_extensions('private/user/edit_user.html', lang=get_locale(), item=item)


@bp.route('/user', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def create_user():
    logger.debug('create_user')
    register_form = CreateFormRegistration(request.form, csrf_enabled=False)
    if register_form.validate_on_submit():
        logger.info('Creating new user ; user_name: {}'.format(register_form.username.data))

        user = User(username=register_form.username.data, email=register_form.email.data, password=register_form.password.data, alias_ar=register_form.alias_ar.data,
                    alias_en=register_form.alias_en.data, active=True)
        role_name = register_form.role_list.data
        try:
            role = Role.query.filter_by(name=role_name.lower()).one()
            user.role_list.append(role)
        except Exception as e:  # TODO manage properly
            logger.warning(traceback.print_exc())
        user.save()

        flash(_l("Thank you for registering. You can now log in."), _l('success'))

        return redirect(url_for('public.home'))
    else:
        flash_errors(register_form)

    return render_extensions('private/user/create_user.html', register_form=register_form)
