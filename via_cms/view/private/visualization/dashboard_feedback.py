"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#
import traceback

from flask import Blueprint
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_feedback import itemize_feedback

logger = LoggerManager.get_logger('dashboard_feedback')

bp = Blueprint('private.visualization.dashboard_feedback', __name__, url_prefix='/private/detail/', static_folder="../static")


@bp.route("/feedback", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def dashboard_feedback(page=None):
    """
    """
    pass  # TODO


@bp.route("/feedback/<feedback_id>", methods=["GET"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def detail_feedback(feedback_id: str):
    """
    """
    item = None
    try:
        id = int(feedback_id)
        item = itemize_feedback(id)
    except ValueError as e:
        logger.warning(traceback.print_exc())  # TODO exception

    return render_extensions("private/feedback/detail_feedback.html", lang=get_locale(), item=item)
