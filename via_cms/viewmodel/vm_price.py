#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import datetime as dt
import decimal
import json

from flask import current_app
from flask_login import current_user
from sqlalchemy import func
from via_common.multiprocess.logger_manager import LoggerManager

from via_cms.extension import db
from via_cms.model._relationship import GeolocPost
from via_cms.model.feed.basket_dao import Basket
from via_cms.model.feed.feed_dao import ID_FINANCE
from via_cms.model.feed.feed_finance_dao import FeedFinance
from via_cms.model.feed.price_dao import Price
from via_cms.model.internal import IdManagerPrice
from via_cms.model.internal._id_manager import IdManagerPost
from via_cms.model.internal.user_dao import User
from via_cms.model.internal.workflow_dao import Workflow
from via_cms.model.static.geoloc_dao import Geoloc
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.status_dao import Status
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale


logger = LoggerManager.get_logger('vm_price')

def price_data_retrieve(subject_id, geoloc_id, language):
    """
    Returns a page of slugs
    """

    subject = Subject.query.get(subject_id)
    if not subject:
        raise AttributeError('Subject_id is not valid: {}'.format(subject_id))

    geoloc = Geoloc.query.get(geoloc_id)
    if not subject:
        raise AttributeError('Geoloc_id is not valid: {}'.format(geoloc_id))

    # By definition, there is only one finance id for a subject and geoloc
    finance = db.session.query(FeedFinance).join(GeolocPost) \
        .filter(FeedFinance.subject_id == subject_id,
                FeedFinance.id == GeolocPost.post_id,
                GeolocPost.geoloc_id == geoloc_id,
                GeolocPost.post_version == FeedFinance.version) \
        .group_by(FeedFinance.id, FeedFinance.version, GeolocPost.geoloc_id) \
        .order_by(FeedFinance.id, FeedFinance.version.desc()) \
        .first()

    if not finance:
        finance_id = IdManagerPost.get_next_id()
        version = 0
        created = dt.datetime.utcnow()
        updated = dt.datetime.utcfromtimestamp(0)
        issued = dt.datetime.utcfromtimestamp(0)
        profile = Profile.query.filter_by(name='price').one()
        status = Status.query.filter_by(name='usable').one()
        workflow = Workflow.query.filter_by(name='created').one()
        # technically speaking it is like the finance post was initialised by the admin
        # TODO currency + language
        finance = FeedFinance(feed_id=ID_FINANCE, id=finance_id, version=version, created=created, updated=updated, issued=issued,
                              profile_id=profile.id, subject_id=subject_id, status_id=status.id, workflow_id=workflow.id,
                              user_id=0, language=language, currency='SYP')
        finance.geoloc_list.append(geoloc)
        try:
            finance.save(commit=False)
        except Exception as e:
            IdManagerPost.query.filter_by(id=finance_id).delete()
            db.session.rollback()
            raise RuntimeError('{}\n'.format(str(e)))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            IdManagerPost.query.filter_by(id=finance_id).delete()
            db.session.commit()
            RuntimeError('{}\n'.format(str(e)))
    # end if finance

    price_list = db.session.query(Basket, Price) \
        .outerjoin(Price,
                   db.and_(Basket.id == Price.basket_id, Price.finance_id == finance.id, Price.version == finance.version)) \
        .filter(Basket.subject_id == subject_id)

    finance_previous = None
    if finance.version > 0:
        finance_previous = FeedFinance.query.filter_by(id=finance.id, version=finance.version - 1).first()

    price_list_previous = None
    if finance_previous:
        price_list_previous = db.session.query(Basket, Price) \
            .outerjoin(Price,
                       db.and_(Basket.id == Price.basket_id,
                               Price.finance_id == finance.id,
                               Price.version == finance_previous.version)) \
            .filter(Basket.subject_id == subject_id)
        price_list_previous = {basket.id: price for basket, price in price_list_previous}

    lang = get_locale()
    price_list_blob = []

    for basket, price in price_list:  # price can be None
        status = finance.status
        status_name = status.name
        workflow = finance.workflow
        workflow_name = workflow.name
        user_id = finance.user_id
        editor = User.query.get(user_id)
        status_label = ''
        workflow_label = ''
        label = ''
        publisher_alias = ''
        if lang == 'ar':
            status_label = status.label_ar
            workflow_label = workflow.label_ar
            label = basket.label_ar
            publisher_alias = editor.alias_en
        elif lang == 'en':
            status_label = status.label_en
            workflow_label = workflow.label_en
            label = basket.label_en
            publisher_alias = editor.alias_en

        price_previous = None
        if finance_previous:
            price_previous = price_list_previous[basket.id]
        # end if finance_previous

        price_id = price.id if price else price_previous.id if price_previous else None
        price_value = price.value if price else None

        finance_published = None
        price_published = None
        if price_id and price_previous:
            # price_previous might or might not be the previous published (as some are optional).
            if price_previous.value is not None:
                price_published = price_previous
                finance_published = finance_previous
            elif price_previous.version > 0:
                price_published = _query_price_published_with_value(price.id if price else price_previous.id, finance)
                if price_published:
                    finance_published = price_published.finance
                # end if price_published and len(price_published) > 0
            # end if price_previous.value is not None
        # end if price_id and price_value is None


        published_value = None
        price_variation = price.variation if price else ''
        published_version = ''
        published_date = ''
        published_time = ''
        editor_published_alias = ''
        editor_updating_alias = ''
        if finance_published:
            published_value = price_published.value
            price_variation = price_variation if price_variation else price_published.variation
            published_version = price_published.version
            published_date = finance_published.issued.strftime('%y/%m/%d')
            published_time = finance_published.issued.strftime('%Hh%M')
            if lang == 'ar':
                editor_published_alias = finance_published.user.alias_en if finance_published.user else ''
            elif lang == 'en':
                editor_published_alias = finance_published.user.alias_en if finance_published.user else ''
            if finance.workflow.name != 'published':
                if lang == 'ar':
                    editor_updating_alias = finance.user.alias_en if finance.user else ''
                elif lang == 'en':
                    editor_updating_alias = finance.user.alias_en if finance.user else ''
            else:
                editor_updating_alias = editor_published_alias

            # end if lang ==...
        # end if price_published

        price_list_blob.append({
            'basket_id': basket.id,
            'id': price_id if price_id is not None else '',
            'version': finance.version,
            'published_version': published_version,
            'updated_date': finance.updated.strftime('%y/%m/%d'),
            'updated_time': finance.updated.strftime('%Hh%M'),
            'issued_date': finance.issued.strftime('%y/%m/%d'),
            'issued_time': finance.issued.strftime('%Hh%M'),
            'published_date': published_date,
            'published_time': published_time,
            'editor_updating_alias': editor_updating_alias,
            'editor_published_alias': editor_published_alias,
            'publisher_alias': publisher_alias,
            'status_name': status_name,
            'status_label': status_label,
            'workflow_name': workflow_name,
            'workflow_label': workflow_label,
            'label': label,
            'unit': basket.unit if basket.unit else '',
            'optional': basket.optional if basket.optional else 0,
            'value': round(float(price_value), 2) if price_value is not None else '',
            'currency': finance.currency if price and finance.currency else 'SYP',
            'variation': '{} %'.format(round(price_variation, 2)) if price_variation else '',
            'published_value': round(float(published_value), 2) if published_value is not None else ''
            })
    # end for basket, price in price_list
    if price_list_blob:
        price_list_blob = sorted(price_list_blob, key=lambda x: x['label'])
    # end if price_list_blob
    header = {
        'finance_id': finance.id,
        'finance_version': finance.version,
        'subject_id': subject.id,
        'subject_name': subject.name
        }

    return header, price_list_blob


def price_data_save(finance_id, finance_version, language, value_list):
    # price.version equals finance.version by definition
    finance = FeedFinance.query.filter_by(id=finance_id, version=finance_version).first()
    if not finance:
        raise AttributeError('Finance should exist before calling price_data_save')

    new_price_list = []
    for metadata, value_str in value_list.items():
        basket, price, price_id, error = _price_data_parse_header(finance, metadata)

        if basket and not error:
            value, error = _price_data_validate_value(basket, value_str)
        if error:
            # in case of error it is better to give up the whole save process instead of saving partially.
            return error

        # So we have the couples: price/finance, price_published/finance_published
        # two cases price does not exist yet (for version 0) or it does.
        price_published = None
        if price_id is not None:
            price_published = _query_price_published_with_value(price_id, finance)  # not necessarily the previous one
        # end if price_id
        if price:  # for the current version, which usually is new
            price, error = _price_update_value(price, price_published, value)
        else:
            _, error = _price_create(price_id, price_published, basket, finance, value)
        # end if price
        if error:
            db.session.rollback()
            return error
        # end if error
    # end for metadata, value_str in value_list.items()

    try:
        finance.save(commit=False)
    except Exception as e:
        db.session.rollback()
        error = '{}\n'.format(str(e))  # TODO
        return error

    # once all the prices have been saved, finance is updated with the prices if they are new and
    # the workflow status is updated.
    _, finance, error = _finance_update_workflow(finance, 'draft')
    if error:
        db.session.rollback()
        return error

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        IdManagerPost.query.filter_by(id=finance_id).delete()
        db.session.commit()
        error = '{}\n'.format(str(e))  # TODO

    return error


def price_data_update_workflow(finance_id, finance_version, language, value_list, workflow_name):
    """
    Sets the current FeedFinance version to published status but it needs to create a new one empty to prepare
    for the next one.
    """

    finance = FeedFinance.query.filter_by(id=finance_id, version=finance_version).first()
    _, _, error = _finance_update_workflow(finance, workflow_name)

    if not error:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.commit()
            error = '{}\n'.format(str(e))  # TODO

    return error


def price_data_publish(finance_id, finance_version, language, value_list):
    finance_reference = FeedFinance.query.filter_by(id=finance_id, version=finance_version).first()
    finance, finance_next, error = _finance_update_workflow(finance_reference, 'published')

    # Now, send the price to the broker if all ok
    if not error and finance.price_list and len(finance.price_list) > 0:
        try:
            # Prepare the content
            content_dict_array = [p.to_dict() for p in finance.price_list if p.value is not None]
            # Form the json message from a template
            content = header_as_dict(finance, content_dict_array, finance.geoloc_list[0])
            # Wrap the message metadata
            content_profile = int(finance.profile_id).to_bytes(4, byteorder='little', signed=True)
            if not error:
                logger.warning('Publish FINANCE: finance_is: {}, finance_version: {}'.format(finance_id, finance_version))
                # item_id = int(0).to_bytes(8, byteorder='little', signed=True)
                # Send the message   # ToDo should be sync
                result, error = current_app.forwarder.send_data_sync(json.dumps(content).encode())
            # end if not error
        except Exception as e:
            db.session.rollback()
            error = '{}\n'.format(e)  # TODO
    # end not error and finance.price_list and len(finance.price_list) > 0

    if not error:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = '{}\n'.format(str(e))  # TODO
        # end try db.session.commit()
    else:
        logger.warning('ERROR during Publish FINANCE: finance_is: {}, finance_version: {}'.format(finance_id, finance_version))
        db.session.rollback()
    # end if not error
    return error

#
# Private definitions.
#

def _price_data_parse_header(finance, value_list):
    error = ''
    basket_id, price_id, price_version = None, None, None
    try:
        basket_id, price_id, price_version = (int(x) if x != 'None' and x != '' else None for x in value_list.split(';'))
    except:  # TODO maybe manage ValueError
        error = 'Invalid result key on "price basket id;price id": {}.\n'.format(value_list)

    basket = None
    if basket_id is not None:
        basket = Basket.query.get(basket_id)
    if not basket:
        return None, None, None, 'Invalid basket id {}. Please contact the dev team'.format(basket_id)

    price = None
    if price_id is not None and price_version is not None:
        price = Price.query.filter_by(id=price_id, version=price_version).first()

    return basket, price, price_id, error


def _query_price_published_with_value(price_id, finance):
    """
    Query le last price published that has a value.
    Can return None.
    """
    if price_id is None:
        raise AttributeError('_query_price_published_with_value - price cannot be None')

    workflow_published = Workflow.query.filter_by(name='published').first()
    last_published = db.session.query(Price, func.max(Price.version)) \
        .join(FeedFinance, db.and_(Price.id == price_id,
                                   Price.value.isnot(None),
                                   Price.version == FeedFinance.version,
                                   Price.finance_id == FeedFinance.id,
                                   FeedFinance.workflow_id == workflow_published.id)) \
        .group_by(Price.id, Price.version).order_by(Price.id, Price.version.desc()).first()  # the group by is necessary for mysql.
    price_published = None
    if last_published and len(last_published) > 0:
        price_published = last_published[0]
    return price_published


def _price_data_validate_value(basket, value_str):
    if not value_str and basket.optional:
        # no error as this price is optional
        return None, ''

    value = Price.VALUE_INVALID
    if value_str:
        try:
            value = float(value_str)
        except:
            return Price.VALUE_INVALID, 'Invalid format for price basket Id: {}, value :{}\n'.format(basket.id, value_str)
        # end try: value = float(v)
        if value < 0:
            return Price.VALUE_INVALID, 'Negative value for price basket Id: {}, value :{}\n'.format(basket.id, value_str)
        # End if value < 0
    # end if value_str

    return value, ''


def _price_create(price_id, price_published, basket, finance, value):
    if value == Price.VALUE_INVALID:
        raise AttributeError('Value is invalid')

    version = finance.version
    is_new_price = False
    variation = 0
    if price_id is None:
        # TODO check it is indeed a new price
        is_new_price = True
        price_id = IdManagerPrice.get_next_id()
    elif value is not None and price_published and price_published.value > 0:
        variation = round(value / float(price_published.value) - 1, 4) * 100

    price = Price(id=price_id, version=version, basket_id=basket.id, finance_id=finance.id, value=value, variation=variation)

    error = ''
    try:
        price.save(commit=False)
    except Exception as e:
        db.session.rollback()
        if is_new_price:
            IdManagerPost.query.filter_by(id=price_id).delete()
            db.session.commit()
        error = '{}\n'.format(str(e))  # TODO

    return price, error


def _price_update_value(price, price_published, value):
    if value == Price.VALUE_INVALID:
        raise AttributeError('Value should not be invalid at this point')

    # updating a value does not create a new entry in the table as this is managed at the FeedFinance level.
    # When publishing then a new version of the FeedFinance is created with the previous price_list
    variation = 0
    if value is not None and price_published and price_published.value > 0.1:
        # For simplification the variation is in regards to the price_published value, therefore 100 -> 101 has a variation of 1%
        # While the definition of variation should be in regards to value now to get the last value (i.e. 100 -> 101 has a var of 0.99%)
        variation = round(value / float(price_published.value) - 1, 4) * 100

    price.value = value
    price.variation = variation
    error = ''
    try:
        price.save(commit=False)
    except Exception as e:
        db.session.rollback()
        error = '{}\n'.format(str(e))  # TODO

    return price, error


def _finance_update_workflow(finance, workflow_name):
    """
    The workflows: 'draft', 'pending' and 'pushed_back', do not create a new version of the finance object,
    while 'publish' do. This looses some information, but for the sake of the db it is better to keep only the
    published post and the last updated draft.
    """
    workflow = Workflow.query.filter_by(name=workflow_name).first()
    if not workflow:
        raise AttributeError('Invalid workflow name')

    error = ''
    finance_next = finance
    if workflow.name == 'draft' or workflow.name == 'pending' or workflow.name == 'pushed_back':
        utc_now = dt.datetime.utcnow()
        if workflow.name == 'draft':
            finance_next.updated = utc_now  # this is a new value
        # just update the fields and return the current model
        finance_next.issued = utc_now
        finance_next.workflow_id = workflow.id
        finance_next.user_id = current_user.id
    elif workflow.name == 'published':
        # It is not possible just to update the primary key, so we need to kind of clone the object.
        finance_id = finance.id
        version = finance.version + 1
        created = finance.created
        updated = finance.updated
        profile_id = finance.profile_id
        status_id = finance.status_id
        subject_id = finance.subject_id
        language = finance.language
        user_id = current_user.id
        utc_now = dt.datetime.utcnow()
        issued = utc_now
        # TODO currency + language
        finance_next = FeedFinance(feed_id=ID_FINANCE, id=finance_id, version=version, created=created, updated=updated, issued=issued,
                                   profile_id=profile_id, subject_id=subject_id, status_id=status_id, workflow_id=workflow.id,
                                   user_id=user_id, language=language, currency='SYP')
        for geoloc in finance.geoloc_list:
            finance_next.geoloc_list.append(geoloc)
        # We still need to update the previous version (the system is not perfect as we do not keep track of all jobs)
        # But this is done on purpose to keep the db small and versions manageable.
        finance.issued = utc_now
        finance.workflow_id = workflow.id
        try:
            finance.save(commit=False)
        except TypeError as e:
            db.session.rollback()
            error = '{}\n'.format(str(e))  # TODO
    # end if workflow.name == 'draft'
    if not error:
        try:
            finance_next.save(commit=False)
        except Exception as e:
            db.session.rollback()
            error = '{}\n'.format(str(e))  # TODO

    return finance, finance_next, error


def header_as_dict(finance, body_dict_array, geoloc):
    # item_id does not make sense for the finance feed as the prices are streamed altogether per subject.
    return {"feed": finance.feed.name,
            "item_id": finance.id,
            "version": finance.version,
            "language": finance.language,
            "currency": finance.currency,
            "created": round(finance.created.replace(tzinfo=dt.timezone.utc).timestamp()),
            "updated": round(finance.updated.replace(tzinfo=dt.timezone.utc).timestamp()),
            "issued": round(finance.issued.replace(tzinfo=dt.timezone.utc).timestamp()),
            "expiry": finance.profile.expiry,
            "status_id": finance.status.id,
            "profile_id": finance.profile_id,
            "profile_name": finance.profile.name,
            "subject_id": finance.subject_id,
            "subject": finance.subject.to_dict(),
            "geoloc_id": geoloc.id,
            "geoloc": geoloc.to_dict(),
            "body_array_json": body_dict_array}
