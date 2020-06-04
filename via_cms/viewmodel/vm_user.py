#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
# 
#
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.internal.user_dao import User

logger = LoggerManager.get_logger('vm_user')

def get_user_list(request_size, page_num):
    """
    Returns a page of slugs
    """

    user_list = User.query.order_by(User.created.asc()).offset(page_num * request_size).limit(request_size)
    user_list_blob = []
    for user in user_list:
        user_list_blob.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created': user.created.strftime('%y/%m/%d - %H:%M:%S'),
            'updated': user.updated.strftime('%y/%m/%d - %H:%M:%S'),
            'last_seen': user.last_seen.strftime('%y/%m/%d - %H:%M:%S') if user.last_seen else '',
            'alias_ar': user.alias_ar,
            'alias_en': user.alias_en,
            'active': user.active
            })
    # end for user in user_list
    return user_list_blob


def itemize_user(user_id):
    """
    Not implemented yet TODO
    """
    item = {}
    user = User.query.get(user_id)
    if user:
        item['user_name'] = user.username
    # end if user
    return item
