#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#


import datetime as dt
import os
import traceback

from flask import Blueprint
from flask import current_app
from flask import flash
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_login import login_required
from werkzeug.utils import secure_filename

from via_cms.extension import db
from via_cms.model import FeedDocument
from via_cms.model.feed.feed_dao import Feed
from via_cms.model.feed.feed_document_dao import FeedDocument
from via_cms.model.internal._id_manager import IdManagerPost
from via_cms.model.internal.workflow_dao import Workflow
from via_cms.model.static.geoloc_dao import Geoloc
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.status_dao import Status
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import check_json, check_mime_type
from via_cms.util.helper import flash_errors
from via_cms.util.helper import get_locale
from via_cms.util.helper import is_rtl
from via_cms.util.helper import render_extensions
from via_cms.util.helper import role_required
from via_cms.view.private.form.create_form_advice import CreateFormAdvice
from via_cms.viewmodel.vm_document import publish_document
from via_common.multiprocess.logger_manager import LoggerManager


logger = LoggerManager.get_logger('editor_document')

bp = Blueprint('private.edition.editor_document', __name__, url_prefix='/private/edition/', static_folder="../static")


@bp.route("/document/<profile_name>/<subject_name>", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def create_document(profile_name, subject_name):
    logger.debug('create_document {}, {}'.format(profile_name, subject_name))
    if profile_name == 'advice':
        form_doc = CreateFormAdvice(subject_name)
        template_slug = 'private/advice/create_advice.html'
        handler = _handle_advice
    else:
        form_doc = CreateFormAdvice(subject_name)
        template_slug = 'private/advice/create_advice.html'
        handler = _handle_advice
    # end if profile_name == 'advice'

    if form_doc.validate_on_submit():
        error = handler(profile_name, subject_name, form_doc)
        if error:
            flash(str(error), category="warning")
            logger.debug(str(error))
        else:
            if profile_name == 'advice':
                flash(_l('The advice has been sent.'), category="success")
            else:
                flash(_l('The advice has been sent.'), category="success")
        # end if error
    else:
        flash_errors(form_doc)

    return render_extensions(template_slug,
                             form_doc=form_doc,
                             lang='"{}"'.format(get_locale()),
                             is_rtl=is_rtl(),
                             profile_name=profile_name,
                             subject_name=subject_name)


def _handle_advice(profile_name, subject_name, form):
    error = ''
    # TODO here we publish directly while we should go through draft first!!!!
    advice_profile = Profile.query.filter_by(name=profile_name).one()
    subject = None
    try:
        subject = Subject.query.filter_by(profile_id=advice_profile.id, name=subject_name).first()
    except Exception as e:
        error += 'Subject {} is not valid\n'.format(subject_name)

    if not error:
        feedback_definition = form.data.get('feedback_definition')
        if feedback_definition:
            feedback_definition = '[{}]'.format(feedback_definition)
            error += check_json(feedback_definition, 'feedback')

    post_id = None
    if not error:
        subject_label = form.subject.text  # the one from the form is already language specific
        language = form.data.get('language')
        title = subject_label
        headline = form.data.get('headline')
        caption = form.data.get('caption')
        more_info = form.data.get('more_info')
        if more_info and more_info.lower().find('https://') == -1 and more_info.lower().find('http://') == -1:
            error = _l('"More info" field is not set properly. It must start with: "http://" or "https://"')
            return error

        post_id = IdManagerPost.get_next_id()
        version = 1
        rendition_main = form.rendition_main.data
        if hasattr(rendition_main, 'filename') and rendition_main.filename:
            rendition_format, error = check_mime_type(rendition_main)
            if error:
                return error
            # end if error
            filename = '{}_{}_{}_{}_{}'.format(profile_name, 'main', post_id, version, secure_filename(rendition_main.filename))
            filename = secure_filename(filename)
            fullpath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], filename)
            rendition_main.filename = filename
            rendition_main.save(fullpath)
            rendition_main_filename = filename
        else:
            error = 'No media attached.'
            return error
        # end if hasattr(rendition_main, 'filename') and rendition_main.filename

        rendition_thumbnail = form.rendition_thumbnail.data
        rendition_thumbnail_filename = None
        if hasattr(rendition_thumbnail, 'filename') and rendition_thumbnail.filename:
            rendition_format, error = check_mime_type(rendition_thumbnail)
            if error:
                return error
            # end if error
            filename = '{}_{}_{}_{}_{}'.format(profile_name, 'thumbnail', post_id, version, secure_filename(rendition_thumbnail.filename))
            filename = secure_filename(filename)
            fullpath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], filename)
            rendition_thumbnail.filename = filename
            rendition_thumbnail.save(fullpath)
            rendition_thumbnail_filename = filename
        # end if hasattr(rendition_thumbnail, 'filename') and rendition_thumbnail.filename

        created = dt.datetime.utcnow()
        updated = created
        issued = created
        status_usable = Status.query.filter_by(name='usable').one()
        workflow_published = Workflow.query.filter_by(name='published').one()
        feed_doc = Feed.query.filter_by(name='document').one()
        advice = FeedDocument(id=post_id, version=version, created=created, updated=updated, issued=issued,
                              profile_id=advice_profile.id, profile=advice_profile, feed_id=feed_doc.id,
                              feed=feed_doc, subject_id=subject.id, subject=subject, status_id=status_usable.id,
                              status=status_usable, workflow_id=workflow_published.id, workflow=workflow_published,
                              user_id=current_user.id,
                              language=language, title=title, headline=headline, caption=caption,
                              feedback_definition=feedback_definition,
                              more_info=more_info, rendition_main_filename=rendition_main_filename,
                              rendition_thumbnail_filename=rendition_thumbnail_filename)
        # add the geoloc
        geoloc_list = []
        geoloc = None
        try:
            geoloc = Geoloc.query.get(1000)  # TODO always Syria for now
        finally:
            if geoloc:
                geoloc_list.append(geoloc)

        # store the advice
        try:
            advice.geoloc_list.extend(geoloc_list)
            advice.save(commit=False)
        except Exception as e:
            error += '{}\n'.format(str(e))  # TODO
        # end try advice.save...

        if not error:
            error += publish_document(advice)
            if not error:
                try:
                    db.session.commit()  # TODO what is commit fails ????
                except Exception as e:
                    error += '{}\n'.format(str(e))  # TODO
                # end try db.session.commit()...
            # end not error
        # end if not error
    # end if not error

    if error:
        db.session.rollback()
        if post_id is not None:
            IdManagerPost.query.filter_by(id=post_id).delete()
            db.session.commit()
    # end if error

    return error



