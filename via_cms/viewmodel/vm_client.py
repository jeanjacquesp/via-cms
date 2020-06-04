#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.monitor.client_dao import Client
from via_cms.util.helper import get_locale

logger = LoggerManager.get_logger('vm_price')

def get_page_client(request_size, page_num, criteria='feedback_last'):
    """
    Returns a page of slugs
    """
    lang = get_locale()
    # TODO for now we are displaying the list of devices. But this should be changed to the list of geoloc_id with a
    #  nb of client>0. We could then even display a map
    # and then the view would have as well a display of lastest feedbacks
    #
    # TODO merge per different dimension: per location (at district level)
    #
    client_list = []
    if criteria == 'feedback_last':
        client_list = Client.query.order_by(Client.feedback_last.asc(), Client.updated.asc())\
            .offset(page_num * request_size).limit(request_size)
    elif criteria == 'updated':
        client_list = Client.query.order_by(Client.updated.asc(), Client.feedback_last.asc())\
            .offset(page_num * request_size).limit(request_size)
    client_list_blob = []
    for client in client_list:
        feedback_nb = len(client.feedback_list)
        feedback_list = {feedback.id: "{}:{}".format(
                feedback.post_id if feedback.post_id else -1, feedback.feedback_json[:48].replace('"', '').replace(' ', '') if feedback.feedback_json else '')
            for feedback in client.feedback_list}
        client_list_blob.append({
            'id': client.id,
            'created': client.created.strftime('%y/%m/%d - %H:%M:%S'),
            'updated': client.updated.strftime('%y/%m/%d - %H:%M:%S'),
            'last_geoloc': client.geoloc_id,  # TODO replace by location label maybe?
            'feedback_nb': feedback_nb,
            'feedback_list': feedback_list,
            'synced_news': client.synced_news.strftime('%y/%m/%d - %H:%M:%S'),
            'synced_finance': client.synced_finance.strftime('%y/%m/%d - %H:%M:%S'),
            'synced_document': client.synced_document.strftime('%y/%m/%d - %H:%M:%S'),
            })

    return client_list_blob
