#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import json

from via_common.multiprocess.logger_manager import LoggerManager

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
        item['client_id'] = feedback.client_id
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
