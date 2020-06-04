"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import traceback

from flask import Blueprint
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_news import get_page_news
from via_cms.viewmodel.vm_news import itemize_news

logger = LoggerManager.get_logger('dashboard_news')

bp = Blueprint('private.visualization.dashboard_news', __name__, url_prefix='/private/dashboard/', static_folder="../static")


@bp.route("/news", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def dashboard_news(page=None):
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

    news_list = []
    try:
        news_list = get_page_news(_page_size, page)
    except Exception as e:
        logger.warning(traceback.print_exc())

    return render_extensions("private/news/dashboard_news.html", lang=get_locale(), news_list=news_list,
                             next_page=next_page, prev_page=prev_page,
                             current=current)


@bp.route("/detail/news/<post_id>", methods=["GET"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def detail_news(post_id: str):
    """
    """

    try:
        id = int(post_id)
        item = itemize_news(id)
    except ValueError as e:
        logger.warning(traceback.print_exc())  # TODO exception
    return render_extensions("private/news/detail_news.html", item=item, id=post_id)
