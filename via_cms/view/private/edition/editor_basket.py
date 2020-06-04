#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import os

from flask import Blueprint
from flask import current_app
from flask import flash
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import func
from via_common.multiprocess.logger_manager import LoggerManager
from werkzeug.utils import secure_filename

from via_cms.extension import db
from via_cms.model.feed.basket_dao import Basket
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.status_dao import Status
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import dao_well_formed
from via_cms.util.helper import flash_errors
from via_cms.util.helper import get_locale
from via_cms.util.helper import is_rtl
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.view.private.form.create_form_basket import CreateFormBasket

logger = LoggerManager.get_logger('editor_basket')

bp = Blueprint('private.edition.editor_basket', __name__, url_prefix='/private/edition/', static_folder="../static")


@bp.route("/basket", methods=["GET", "POST"])
@login_required
@role_required(['supervisor', 'admin'])
def create_basket():
    logger.debug('create_basket')
    form_basket = CreateFormBasket()
    if form_basket.validate_on_submit():
        # TODO move to vm
        error = ''

        label_en = form_basket.data.get('label_en').strip()
        name = label_en.replace(' and ', '_').replace(' or ', '_').replace(',', '_').replace('.', '_').replace(' ',
                                                                                                               '_').lower()
        if not dao_well_formed(name):
            error += "Label in english: "
            {}
            ", is not well formed.\n"
        basket = Basket.query.filter_by(name=name).first()
        if basket:
            error += "Label in english: "
            {}
            ", cannot be resolved as a unique technical name for the product.\n"
        profile_price_id = Profile.query.filter_by(name='price').one().id
        status_usable_id = Status.query.filter_by(name='usable').one().id
        subject_name = form_basket.data.get('subject')
        subject = None
        try:
            subject_obj = Subject.query.filter_by(profile_id=profile_price_id, name=subject_name).all()
            if subject_obj and len(subject_obj) == 1:
                subject = subject_obj[0]
            else:
                error += 'An unknown error happened while resolving the subject\n'
        except:
            error += 'Subject {} is not valid\n'.format(subject_name)

        code = db.session.query(func.max(Basket.code)).filter(Basket.subject_id == subject.id).first()[0] + 1
        label_ar = form_basket.data.get('label_ar')
        unit = form_basket.data.get('unit')
        description_ar = form_basket.data.get('description_ar')
        description_en = form_basket.data.get('description_en')
        rendition_file = form_basket.rendition_file.data
        if hasattr(rendition_file, 'filename') and rendition_file.filename:
            filename = secure_filename(rendition_file.filename)
            # TODO define upload directory
            # TODO check filename already exist
            fullpath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], filename)
            rendition_file.save(fullpath)
            # f = open(fullpath, "rb")
            # data = f.read()
            # rendition_blob = base64.b64encode(data)
            # rendition_blob = data64.decode("UTF-8")
            rendition_filename = filename
        else:
            rendition_filename = None

        if not error:
            # create the basket
            basket = Basket(status_id=status_usable_id, subject_id=subject.id, code=code,
                                  user_id=current_user.id,
                                  name=name, label_ar=label_ar, label_en=label_en, unit=unit,
                                  description_ar=description_ar, description_en=description_en,
                                  rendition_filename=rendition_filename, profile_id=profile_price_id)
            # store the basket
            try:
                basket.save(commit=False)
            except Exception as e:
                db.session.rollback()
                error += '{}\n'.format(str(e))  # TODO

            if not error:
                db.session.commit()
                # current_user.basket_list.append(basket)
                # current_user.save()  # TODO rollback basket in case of error
                flash(_l('The price basket has been updated.'), category="success")
        if error:
            flash(str(error), category="warning")
    else:
        flash_errors(form_basket)
    return render_extensions('private/basket/create_basket.html',
                             form_basket=form_basket, lang='"{}"'.format(get_locale()),
                             is_rtl=is_rtl())

