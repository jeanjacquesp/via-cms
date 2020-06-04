"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from flask import Blueprint
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_client import get_page_client

logger = LoggerManager.get_logger('dashboard_client')

bp = Blueprint('private.visualization.dashboard_client', __name__, url_prefix='/private/dashboard/', static_folder="../static")


@bp.route("/client", methods=["GET", "POST"])
@login_required
@role_required(['supervisor', 'admin'])
def dashboard_client(page=None):
    """
    """

    page = int(page) if page else 0
    _page_size = 100  # TODO: selectable on html

    if not page or page <= 0:
        next_page = 0
        prev_page = 1
        current = True
    else:
        next_page = page - 1
        prev_page = page + 1
        current = False

    client_list = get_page_client(_page_size, page)

    return render_extensions("private/client/dashboard_client.html", lang=get_locale(), client_list=client_list,
                             next_page=next_page, prev_page=prev_page,
                             current=current)


@bp.route("/detail/client/<client_id>", methods=["GET"])
@login_required
def detail_client(client_id: str):
    """
    """
    pass
    # post = get_post_detail(int(client_id))
    # return render_extensions("private/client/detail_client.html", post=post)
