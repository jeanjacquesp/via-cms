#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import traceback

from flask import Blueprint
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_user import itemize_user

logger = LoggerManager.get_logger('detail_user')

bp = Blueprint('private.user.detail_user', __name__, url_prefix='/private/admin/detail/', static_folder="../static")


@bp.route("/user/<user_id>", methods=["GET"])
@login_required
@role_required(['admin'])
def detail_user(user_id: str):
    # TODO add this the user dashboard
    try:
        id = int(user_id)
        item = itemize_user(id)
    except ValueError as e:
        logger.warning(traceback.print_exc())  # TODO exception
    return render_extensions("private/user/profile_user.html", item=item)


@bp.route("/my_profile", methods=["GET"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def detail_user_current():
    return render_extensions("private/user/profile_user_current.html")
