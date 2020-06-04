#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import json
import traceback

from flask import current_app
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.feed.feed_document_dao import FeedDocument
from via_cms.model.feed.feed_post_dao import FeedPost
from via_cms.model.internal.user_dao import User
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale


logger = LoggerManager.get_logger('vm_document')


def get_page_document(request_size, page_num):
    """
    Returns a page of slugs
    """
    lang = get_locale()
    doc_list = FeedDocument.query.order_by(FeedDocument.created.asc()).offset(page_num * request_size).limit(request_size)
    doc_list_blob = []
    for doc in doc_list:
        editor = ''
        subject_label = ''
        feedback_nb = len(doc.feedback_list)
        feedback_list = ', '.join(("{}".format(x.id) for x in doc.feedback_list))
        status_label = ''
        workflow_label = ''
        profile_label = ''
        geotag = ''
        if lang == 'ar':
            status_label = doc.status.label_ar
            workflow_label = doc.workflow.label_ar
            subject_label = doc.subject.label_ar
            profile_label = doc.profile.label_ar
            geotag = '; '.join((x.label_ar for x in doc.geoloc_list))
            editor = doc.editor.alias_ar
        elif lang == 'en':
            status_label = doc.status.label_en
            workflow_label = doc.workflow.label_en
            subject_label = doc.subject.label_en
            profile_label = doc.profile.label_en
            geotag = '; '.join((x.label_en for x in doc.geoloc_list))
            editor = doc.editor.alias_en
        geoloc_id_list = '; '.join((str(x.id) for x in doc.geoloc_list))
        doc_list_blob.append({
            'id': doc.id,
            'version': doc.version,
            'language': doc.language,
            'title': doc.title[:30] + " ..." if doc.title and len(doc.title) > 34 else doc.title,
            'created_date': doc.created.strftime('%y/%m/%d'),
            'updated_date': doc.updated.strftime('%y/%m/%d'),
            'updated_time': doc.updated.strftime('%H:%M:%S'),
            'editor': editor,
            'status_label': status_label,
            'workflow_label': workflow_label,
            'subject_label': subject_label,
            'profile_label': profile_label,
            'geotag': geotag,
            'geoloc_id_list': geoloc_id_list,
            'caption': doc.caption[:18] + " ..." if doc.caption
                                                      and len(doc.caption) > 22 else doc.caption,
            'headline': doc.headline[:30] + " ..." if doc.headline
                                                      and len(doc.headline) > 34 else doc.headline,
            'feedback_nb': feedback_nb,
            'feedback_list': feedback_list
        })

    return doc_list_blob


def itemize_document(post_id):
    lang = get_locale()

    item = {}

    post = FeedPost.query.filter_by(id=post_id).one()
    doc = FeedDocument.query.filter_by(id=post_id).one()

    from via_cms.main import get_config_flask
    config_flask = get_config_flask()

    if post and doc:
        item['post_id'] = str(post.id)
        item['created'] = post.created
        item['updated'] = post.updated
        item['posted'] = post.created.strftime("%a %d %B %Y - %H:%M")
        item['lang'] = doc.language
        item['title'] = doc.title
        item['headline'] = doc.headline
        item['caption'] = doc.caption
        item['more_info'] = doc.more_info
        item['feedback_definition'] = doc.feedback_definition
        item['rendition_thumbnail_filename'] = doc.rendition_thumbnail_filename if doc.rendition_thumbnail_filename else ''
        item['rendition_main_filename'] = doc.rendition_main_filename
        profile = Profile.query.get(post.profile_id)
        item['profile_name'] = profile.name
        if lang == 'ar':
            item['profile'] = profile.label_ar
        elif lang == 'en':
            item['profile'] = profile.label_en
        subject = Subject.query.get(post.subject_id)
        item['subject_name'] = subject.name
        if lang == 'ar':
            item['subject'] = subject.label_ar
        elif lang == 'en':
            item['subject'] = subject.label_en
        item['status_name'] = doc.status.name
        if lang == 'ar':
            item['status'] = doc.status.label_ar
        elif lang == 'en':
            item['status'] = doc.status.label_en
        user = User.query.get(post.user_id)
        item['user_id'] = user.id
        if lang == 'ar':
            item['user'] = user.alias_ar + " - " + user.alias_en
        elif lang == 'en':
            item['user'] = user.alias_en + " - " + user.alias_ar
        geoloc_list = {}
        for geoloc in doc.geoloc_list:
            label = ''
            if lang == 'ar':
                label = geoloc.label_ar
            elif lang == 'en':
                label = geoloc.label_en
            geoloc_list.update({geoloc.id: label})
        item['geoloc_list'] = geoloc_list
    else:
        item['error'] = "Document " + post_id + " Not found"  # TODO manage error properly

    return item


# TODO splitting here between geoloc is not optimal :(
def publish_document(doc, topic_prefix=''):
    error = ''
    if doc:
        try:
            result = doc.to_dict_of_dict_by_geoloc()
            # content_profile = int(doc.profile.id).to_bytes(4, byteorder='little', signed=True)
            # item_id = int(doc.id).to_bytes(8, byteorder='little', signed=True)
            logger.debug('Publishing {}: post_id: {}'.format(doc.profile.name, doc.id))
            for geoloc_id, content in result.items():
                # TODO should be a future...
                _, error = current_app.forwarder.send_data_sync(json.dumps(content).encode())
        except ValueError as e:
            error += '{}\n'.format(str(e))  # TODO exception
            traceback.print_tb(e.__traceback__)
        except Exception as e:
            error += '{}\n'.format(str(e))  # TODO exception
            traceback.print_tb(e.__traceback__)

    return error
