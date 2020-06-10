#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import json

from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model import FeedPost
from via_cms.model import Profile
from via_cms.model.monitor.feedback_dao import Feedback
from via_cms.util.helper import get_locale
from via_cms.util.helper import json2html

logger = LoggerManager.get_logger('vm_feedback')

def itemize_feedback(feedback_id: int):
    lang = get_locale()

    item = {}

    feedback = Feedback.query.get(feedback_id)

    error = ''
    if feedback:
        item['feedback_id'] = str(feedback.id)
        item['created'] = feedback.created
        item['updated'] = feedback.updated
        item['post_id'] = feedback.post_id
        item['post_version'] = feedback.post_version
        if feedback.post_id and feedback.post_version:
            post = FeedPost.query.get((feedback.post_id, feedback.post_version))
            item['profile_id'] = post.profile_id if post.profile_id else ''
            item['profile_name'] = Profile.query.get(post.profile_id).name if post.profile_id else ''
            item['subject_id'] = post.subject_id if post.subject_id else ''
            # if post.profile_id == Profile.query.filter_by(name='price').one().id:

        try:
            item['feedback'] = json2html(feedback.feedback_json)  # TODO link them to feedback widget...
            # item['feedback'] = json.loads(feedback.feedback) # TODO link them to feedback widget...
        except json.JSONDecodeError as e:
            error += str(e)
    else:
        error = "Notice " + str(feedback_id) + " Not found"  # TODO manage error properly

    if error:
        item['error'] = error

    return item
