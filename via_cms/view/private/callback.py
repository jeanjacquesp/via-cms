#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import json
import datetime as dt

from flask import Blueprint
from flask import flash
from flask import request
from flask_login import current_user
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.extension import bcrypt
from via_cms.model.internal.user_dao import User
from via_cms.model.static.geoloc_dao import Geoloc
from via_cms.util.helper import get_locale, check_pwd_complexity
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_price import price_data_publish
from via_cms.viewmodel.vm_price import price_data_retrieve
from via_cms.viewmodel.vm_price import price_data_save
from via_cms.viewmodel.vm_price import price_data_update_workflow

logger = LoggerManager.get_logger('callback')

bp = Blueprint('private.callback', __name__, static_folder="../static")

#
# COMMON
#

@bp.route("/private/get_geoloc_tree", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'], do_flash=False)
def get_geoloc_tree():
    geoloc_list = current_user.get_geoloc_rights()
    return Geoloc.build_fancytree_json_tree(get_locale(), geoloc_list)

#
# PRICE
#

@bp.route("/private/editor_price_retrieve", methods=["POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'], do_flash=False)
def editor_price_retrieve():
    data = json.loads(request.data)

    try:
        geoloc_id = int(data.get('geoloc_id', -1))
    except:
        geoloc_id = -1 # TODO

    try:
        subject_id = int(data.get('subject_id', -1))
    except:
        subject_id = -1 # TODO
    try:
        language = int(data.get('language', ''))
    except:
        language = 'ar'  # TODO

    header = ''
    price_list = {}
    try:
        header, price_list = price_data_retrieve(subject_id, geoloc_id, language)
    except Exception as e:
        flash(str(e), category="error")

    return render_extensions('private/price/table_price.html', header=header, price_list=price_list)


@bp.route("/private/editor_price_save", methods=["POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'], do_flash=False)
def editor_price_save():
    data = json.loads(request.data)

    try:
        finance_id = int(data.get('finance_id', -1))
    except:
        finance_id = -1

    try:
        finance_version = int(data.get('finance_version', -1))
    except:
        finance_version = -1

    value_list = data.get('value_list', {})
    language = data.get('language', {})

    try:
        error = price_data_save(finance_id, finance_version, language, value_list)
    except Exception as e:
        error = 'System error. Please contact the dev team. The error is:\n{}'.format(e)
        logger.warning(error)

    return error if error else 'ok'


@bp.route("/private/editor_price_validate", methods=["POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'], do_flash=False)
def editor_price_validate():
    data = json.loads(request.data)

    try:
        finance_id = int(data.get('finance_id', -1))
    except:
        finance_id = -1

    try:
        finance_version = int(data.get('finance_version', -1))
    except:
        finance_version = -1

    value_list = data.get('value_list', {})
    language = data.get('language', {})

    error = price_data_update_workflow(finance_id, finance_version, language, value_list, 'pending')

    return error if error else 'ok'


@bp.route("/private/editor_price_publish", methods=["POST"])
@login_required
@role_required(['supervisor', 'admin'], do_flash=False)
def editor_price_publish():
    data = json.loads(request.data)

    try:
        finance_id = int(data.get('finance_id', -1))
    except:
        finance_id = -1

    try:
        finance_version = int(data.get('finance_version', -1))
    except:
        finance_version = -1

    value_list = data.get('value_list', {})
    language = data.get('language', {})

    error = price_data_publish(finance_id, finance_version, language, value_list)

    return error if error else 'ok'


@bp.route("/private/editor_price_reject", methods=["POST"])
@login_required
@role_required(['supervisor', 'admin'], do_flash=False)
def editor_price_reject():
    data = json.loads(request.data)

    try:
        finance_id = int(data.get('finance_id', -1))
    except:
        finance_id = -1

    try:
        finance_version = int(data.get('finance_version', -1))
    except:
        finance_version = -1

    value_list = data.get('value_list', {})
    language = data.get('language', {})

    error = price_data_update_workflow(finance_id, finance_version, language, value_list, 'pushed_back')

    return error if error else 'ok'


@bp.route("/private/dashboard_user_change_active", methods=["POST"])
@login_required
@role_required(['supervisor', 'admin'], do_flash=False)
def dashboard_user_change_active():
    res = ''
    error = ''
    data = json.loads(request.data)
    user_id = data.get('user_id', -1)
    if user_id == 0:
        return 'This profile is protected'
    if user_id == current_user.id:
        return 'Users cannot change the status of their own account'

    user = User.query.get(user_id)
    if user:
        if user.active:
            user.active = False
        else:
            user.active = True
        user.updated = dt.datetime.utcnow()
        user.save()
        user = User.query.get(user_id)
        active = user.active
        res = {'active': active, 'status': 'ok'}
        logger.info('Updated status to {} for user ; user_id: {}, username: {}'.format(user.active, user.id, user.username))

    return error if error else res


@bp.route("/private/dashboard_user_change_password", methods=["POST"])
@login_required
@role_required(['supervisor', 'admin'], do_flash=False)
def dashboard_user_change_password():
    data = json.loads(request.data)
    user_id = data.get('user_id', -1)
    if user_id == 0 and current_user.id != 0:
        return 'This profile is protected'

    new_pass = data.get('new_pass', -1)

    error = check_pwd_complexity(new_pass)
    if error:
        return error

    user = User.query.get(user_id)
    user.password = bcrypt.generate_password_hash(new_pass)
    user.updated = dt.datetime.utcnow()
    user.save()
    user = User.query.get(user_id)
    active = user.active
    res = {'active': active, 'status': 'ok'}
    logger.info('Updated user password ; user_id: {}, username: {}'.format(user.id, user.username))

    return error if error else res


@bp.route("/private/edit_profile", methods=["POST"])
@login_required
@role_required(['supervisor', 'admin'], do_flash=False)
def edit_profile():
    logger.debug('edit_profile')
    error = ''
    data = json.loads(request.data)
    user_id = data.get('user_id', -1)
    alias_ar = data.get('alias_ar', -1)
    alias_en = data.get('alias_en', -1)

    user = User.query.get(user_id)
    user.alias_ar = alias_ar
    user.alias_en = alias_en
    user.updated = dt.datetime.utcnow()
    user.save()
    user = User.query.get(user_id)
    alias_ar = user.alias_ar
    alias_en = user.alias_en
    res = {'alias_ar': alias_ar, 'alias_en': alias_en, 'status': 'ok'}
    logger.info('Edited user profile ; user_id: {}, username: {}'.format(user.id, user.username))


    return error if error else res