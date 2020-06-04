#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.model.feed.basket_dao import Basket
from via_cms.util.helper import get_locale

logger = LoggerManager.get_logger('vm_price')

def get_basket_list(subject_list):
    """
    Returns a page of slugs
    """
    lang = get_locale()

    basket_list_blob = []
    for subject in subject_list:
        basket_list = Basket.query.filter_by(subject_id=subject.id)

        for basket in basket_list:
            subject = basket.subject
            status = basket.status
            status_label = ''
            subject_label = ''
            label = ''
            editor = ''
            if lang == 'ar':
                status_label = status.label_ar
                subject_label = subject.label_ar
                label = basket.label_ar
                editor = basket.editor.alias_ar

            elif lang == 'en':
                status_label = status.label_en
                subject_label = subject.label_en
                label = basket.label_en
                editor = basket.editor.alias_en

            basket_list_blob.append({
                'id': basket.id,
                'status_label': status_label,
                'label': label,
                'unit': basket.unit,
                'created_date': basket.created.strftime('%y/%m/%d'),
                'subject_id': basket.subject_id,
                'code': basket.code,
                'subject_name': basket.subject.name,
                'editor': editor, })

    return basket_list_blob


def get_top_tag_list(n):
    """
    Returns N top tag_list
    """

    raise NotImplementedError


def get_tagged_post_list(tag, limit):
    """
    Gets the most recent limit post_list with a certain tag
    """

    raise NotImplementedError
