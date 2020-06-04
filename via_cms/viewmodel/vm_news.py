#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import datetime as dt
import json
import traceback

from flask import current_app

from via_cms.model.feed.feed_news_dao import FeedNews
from via_cms.model.feed.feed_post_dao import FeedPost
from via_cms.model.internal.user_dao import User
from via_cms.model.internal.workflow_dao import Workflow
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.status_dao import Status
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale
from via_common.multiprocess.logger_manager import LoggerManager

logger = LoggerManager.get_logger('vm_news')

def get_page_news(request_size, page_num):
    """
    Returns a page of slugs
    """
    lang = get_locale()
    news_list = FeedNews.query.order_by(FeedNews.created.asc()).offset(page_num * request_size).limit(request_size)
    news_list_blob = []
    for news in news_list:
        editor = ''
        subject_label = ''
        feedback_nb = len(news.feedback_list)
        feedback_list = ', '.join(("{}".format(x.id) for x in news.feedback_list))
        status_label = ''
        workflow_label = ''
        profile_label = ''
        geotag = ''
        if lang == 'ar':
            status_label = news.status.label_ar
            workflow_label = news.workflow.label_ar
            subject_label = news.subject.label_ar
            profile_label = news.profile.label_ar
            geotag = '; '.join((x.label_ar for x in news.geoloc_list))
            editor = news.editor.alias_ar
        elif lang == 'en':
            status_label = news.status.label_en
            workflow_label = news.workflow.label_en
            subject_label = news.subject.label_en
            profile_label = news.profile.label_en
            geotag = '; '.join((x.label_en for x in news.geoloc_list))
            editor = news.editor.alias_en
        geoloc_id_list = '; '.join((str(x.id) for x in news.geoloc_list))
        news_list_blob.append({
            'id': news.id,
            'version': news.version,
            'language': news.language,
            'title': news.title[:30] + " ..." if news.title and len(news.title) > 34 else news.title,
            'created_date': news.created.strftime('%y/%m/%d'),
            'updated_date': news.updated.strftime('%y/%m/%d'),
            'updated_time': news.updated.strftime('%H:%M:%S'),
            'editor': editor,
            'status_label': status_label,
            'workflow_label': workflow_label,
            'subject_label': subject_label,
            'profile_label': profile_label,
            'geotag': geotag,
            'geoloc_id_list': geoloc_id_list,
            # 'subtitle1': news.subtitle1[:18] + " ..." if news.subtitle1
            #                                                  and len(news.subtitle1) > 22 else news.subtitle1,
            # 'subtitle2': news.subtitle2[:18] + " ..." if news.subtitle2
            #                                                  and len(news.subtitle2) > 22 else news.subtitle2,
            'headline': news.headline[:30] + " ..." if news.headline
                                                           and len(news.headline) > 34 else news.headline,
            'feedback_nb': feedback_nb,
            'feedback_list': feedback_list
            })

    return news_list_blob


def itemize_news(post_id):
    lang = get_locale()

    item = {}

    post = FeedPost.query.filter_by(id=post_id).one()
    news = FeedNews.query.filter_by(id=post_id).one()

    if post and news:
        item['post_id'] = str(post.id)
        item['created'] = post.created
        item['updated'] = post.updated
        item['posted'] = post.created.strftime("%a %d %B %Y - %H:%M")
        item['lang'] = news.language
        item['title'] = news.title
        item['headline'] = news.headline
        item['body_dict'] = json.loads(news.body_json)
        item['contact_dict'] = json.loads(news.contact_json) if news.contact_json else ''
        item['more_info'] = news.more_info
        item['feedback_definition'] = news.feedback_definition
        item['filename'] = news.rendition_thumbnail_filename
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
        item['status_name'] = news.status.name
        if lang == 'ar':
            item['status'] = news.status.label_ar
        elif lang == 'en':
            item['status'] = news.status.label_en
        user = User.query.get(post.user_id)
        item['user_id'] = user.id
        if lang == 'ar':
            item['user'] = user.alias_ar + " - " + user.alias_en
        elif lang == 'en':
            item['user'] = user.alias_en + " - " + user.alias_ar
        geoloc_list = {}
        for geoloc in news.geoloc_list:
            label = ''
            if lang == 'ar':
                label = geoloc.label_ar
            elif lang == 'en':
                label = geoloc.label_en
            geoloc_list.update({geoloc.id: label})
        item['geoloc_list'] = geoloc_list
        item['rendition_thumbnail_filename'] = news.rendition_thumbnail_filename
    else:
        item['error'] = "Notice " + post_id + " Not found"  # TODO manage error properly

    return item


# TODO splitting here between geoloc is not optimal :(
def publish_news_all_geoloc(news, topic_prefix=''):
    error = ''
    if news:
        try:
            result = news.to_dict_of_dict_by_geoloc()
            # content_profile = int(news.profile.id).to_bytes(4, byteorder='little', signed=True)
            # item_id = int(news.id).to_bytes(8, byteorder='little', signed=True)
            logger.debug('Publishing {}: post_id: {}, geoloc_list: {}'
                                     .format(news.profile.name, news.id, str(news.geoloc_list)))
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
