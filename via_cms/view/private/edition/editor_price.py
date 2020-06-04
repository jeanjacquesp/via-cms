"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from collections import namedtuple

from flask import Blueprint
from flask_login import current_user
from flask_login import login_required
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.static.geoloc_dao import CATEGORY_DISTRICT
from via_cms.model.static.geoloc_dao import Geoloc
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required


bp = Blueprint('private.edition.editor_price', __name__, url_prefix='/private/edition/', static_folder="../static")

logger = LoggerManager.get_logger('editor_price')

@bp.route("/price", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def editor_price():
    logger.debug('editor_price')
    """
    """
    profile_id = Profile.query.filter_by(name='price').one().id
    subject_list = Subject.query.filter_by(profile_id=profile_id).order_by(Subject.id.asc())

    lang = get_locale()
    geoloc_list = Geoloc.query.filter_by(category=CATEGORY_DISTRICT)
    subject_list_display = []
    if lang == 'ar':
        subject_list_display = [namedtuple('X', ('id', 'name', 'label'))(sub.id, sub.name, sub.label_ar) for sub in subject_list]
        location_list = [(str(geo.parent_id), geo.parent.label_ar, str(geo.id), geo.label_ar) for geo in geoloc_list]
    elif lang == 'en':
        subject_list_display = [namedtuple('X', ('id', 'name', 'label'))(sub.id, sub.name, sub.label_en) for sub in subject_list]
        location_list = [(str(geo.parent_id), geo.parent.label_en, str(geo.id), geo.label_en) for geo in geoloc_list]

    is_supervisor = False
    for role in current_user.role_list:
        if role.principal in ['admin', 'supervisor']:
            is_supervisor = True

    lang = get_locale()  # TODO add lanague to the html (right now it is hard coded)

    return render_extensions("private/price/editor_price.html", subject_list=subject_list_display,
                             location=location_list, is_supervisor=is_supervisor)
