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
from via_common.multiprocess.logger_manager import LoggerManager
from werkzeug.utils import secure_filename

from via_cms.extension import db
from via_cms.model import ID_NEWS
from via_cms.model.feed.feed_dao import Feed
from via_cms.model.feed.feed_news_dao import FeedNews
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
from via_cms.view.private.form.create_form_bulletin import CreateFormBulletin
from via_cms.view.private.form.create_form_news import CreateFormNews
from via_cms.view.private.form.create_form_notice import CreateFormNotice

from via_cms.viewmodel.vm_news import publish_news_all_geoloc


bp = Blueprint('private.edition.editor_news', __name__, url_prefix='/private/edition/', static_folder="../static")

logger = LoggerManager.get_logger('editor_news')


@bp.route("/news/<profile_name>/<subject_name>", methods=["GET", "POST"])
@login_required
@role_required(['editor', 'supervisor', 'admin'])
def create_news(profile_name, subject_name):
    logger.debug('create_news {}, {}'.format(profile_name, subject_name))

    if profile_name == 'bulletin':
        form_news = CreateFormBulletin(subject_name)
        template_slug = 'private/bulletin/create_bulletin.html'
    elif profile_name == 'notice':
        form_news = CreateFormNotice(subject_name)
        template_slug = 'private/notice/create_notice.html'
    else:
        form_news = CreateFormNews(profile_name, subject_name)
        template_slug = 'private/news/create_news.html'
    # end if profile_name == 'bulletin'

    if form_news.validate_on_submit():
        error = _handle_news(profile_name, subject_name, form_news)
        if error:
            flash(str(error), category="warning")
            logger.warning(error)
        else:
            if profile_name == 'bulletin':
                flash(_l('The bulletin has been sent.'), category="success")
            elif profile_name == 'notice':
                flash(_l('The notice has been sent.'), category="success")
            else:
                flash(_l('The free form news has been sent.'), category="success")
        # end if error
    else:
        flash_errors(form_news)
    # end if form_news.validate_on_submit()



    return render_extensions(template_slug,
                             form_news=form_news,
                             lang='"{}"'.format(get_locale()),
                             is_rtl=is_rtl(),
                             profile_name=profile_name,
                             subject_name=subject_name)


def _handle_news(profile_name, subject_name, form):
    logger.debug('_handle_news')
    error = ''
    # TODO here we publish directly while we should go through draft first!!!!
    bulletin_profile = Profile.query.filter_by(name=profile_name).one()
    subject = None
    try:
        subject = Subject.query.filter_by(profile_id=bulletin_profile.id, name=subject_name).first()
    except Exception as e:
        error += 'Subject {} is not valid\n'.format(subject_name)

    if not error:
        body_json = form.data.get('body_json')
        error += check_json(body_json, 'body')
        feedback_definition = form.data.get('feedback_definition')
        if feedback_definition:
            feedback_definition = '[{}]'.format(feedback_definition)
            error += check_json(feedback_definition, 'feedback')
        contact_json = form.data.get('contact_json')
        if contact_json:
            error += check_json(contact_json, 'contact')

    post_id = None
    if not error:
        version = '1'   # todo
        subject_label = form.subject.text  # the one from the form is already language specific
        language = form.data.get('language')
        title = subject_label
        headline = form.data.get('headline')
        # subtitle1 = title
        # subtitle2 = form.data.get('place')
        more_info = form.data.get('more_info')
        if more_info and more_info.lower().find('https://') == -1 and more_info.lower().find('http://') == -1:
            error = _l('"More info" field is not set properly. It must start with: "http://" or "https://"')
            return error

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

        post_id = IdManagerPost.get_next_id()
        version = 1
        created = dt.datetime.utcnow()
        updated = created
        issued = created
        status_usable = Status.query.filter_by(name='usable').one()
        workflow_published = Workflow.query.filter_by(name='published').one()
        feed_news = Feed.query.filter_by(name='news').one()
        bulletin = FeedNews(id=post_id, version=version, created=created, updated=updated, issued=issued,
                        profile_id=bulletin_profile.id, profile=bulletin_profile, feed_id=feed_news.id,
                        feed=feed_news, subject_id=subject.id, subject=subject, status_id=status_usable.id,
                        status=status_usable, workflow_id=workflow_published.id, workflow=workflow_published,
                        user_id=current_user.id,
                        language=language, title=subject_label, headline=headline,
                        body_json=body_json, feedback_definition=feedback_definition,
                        more_info=more_info, contact_json=contact_json, rendition_thumbnail_filename=rendition_thumbnail_filename)
        # add the geoloc
        geotag_list = [int(x) for x in form.data.get('geotag_list').split(';')]  # TODO? ValueError
        geoloc_list = []
        for geoloc_id in geotag_list:
            geoloc = None
            try:
                geoloc = Geoloc.query.get(geoloc_id)
            finally:
                # do not save children as a geotag includes all its children
                if geoloc and (not geoloc.parent_id or geoloc.parent_id not in geotag_list):
                    geoloc_list.append(geoloc)
            # end try geoloc = Geoloc...
        # end for geoloc_id in geotag_list

        # store the bulletin
        try:
            bulletin.geoloc_list.extend(geoloc_list)
            bulletin.save(commit=False)
        except Exception as e:
            error += '{}\n'.format(str(e))  # TODO
        # end try bulletin.save...

        if not error:
            error += publish_news_all_geoloc(bulletin)
            if not error:
                try:
                    db.session.commit()
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

