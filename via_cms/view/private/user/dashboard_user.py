"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#


from flask import Blueprint
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_user import get_user_list

logger = LoggerManager.get_logger('dashboard_user')

bp = Blueprint('private.user.dashboard_user', __name__, url_prefix='/private/admin/dashboard',
               static_folder="../static")


@bp.route("/user", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def dashboard_user(page=None):
    """
    """

    page = int(page) if page else 0  # TODO !!!! page + ValueError
    _page_size = 100  # TODO: selectable on html

    if not page or page <= 0:
        next_page = 0
        prev_page = 1
        current = True
    else:
        next_page = page - 1
        prev_page = page + 1
        current = False

    user_list = get_user_list(_page_size, page)

    return render_extensions("private/user/dashboard_user.html", lang=get_locale(), user_list=user_list,
                             next_page=next_page, prev_page=prev_page,
                             current=current)

