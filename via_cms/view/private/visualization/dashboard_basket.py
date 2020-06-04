"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from collections import namedtuple

from flask import Blueprint
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.viewmodel.vm_basket import get_basket_list

logger = LoggerManager.get_logger('dashboard_basket')

bp = Blueprint('private.visualization.dashboard_basket', __name__, url_prefix='/private/dashboard/', static_folder="../static")


@bp.route("/basket", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def dashboard_basket(page=None):
    """
    """

    page = int(page) if page else 0 # TODO page + ValueError
    _page_size = 100  # TODO: selectable on html

    if not page or page <= 0:
        next_page = 0
        prev_page = 1
        current = True
    else:
        next_page = page - 1
        prev_page = page + 1
        current = False

    profile_id_price = Profile.query.filter_by(name='price').one().id
    subject_list = Subject.query.filter_by(profile_id=profile_id_price)

    basket_list = get_basket_list(subject_list)

    lang = get_locale()
    if lang == 'ar':
        subject_list = [namedtuple('X', ('name', 'label'))(x.name, x.label_ar) for x in subject_list]
    elif lang == 'en':
        subject_list = [namedtuple('X', ('name', 'label'))(x.name, x.label_en) for x in subject_list]

    return render_extensions("private/basket/dashboard_basket.html", subject_list=subject_list,
                             basket_list=basket_list, next_page=next_page, prev_page=prev_page,
                             current=current)

