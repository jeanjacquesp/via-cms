#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import datetime as dt
import json
from datetime import timedelta

from via_common.util.error import Error

from via_cms.extension import db
from via_cms.model.feed import FeedFinance
from via_cms.model.feed.feed_news_dao import FeedNews
from via_cms.model.internal.workflow_dao import Workflow
from via_cms.model.static.geoloc_dao import CATEGORY_NEIGHBORHOOD
from via_cms.model.static.geoloc_dao import CATEGORY_SUBDISTRICT
from via_cms.model.static.geoloc_dao import Geoloc
from via_cms.model.static.status_dao import Status
from via_cms.viewmodel.vm_price import header_as_dict
from via_common.multiprocess.logger_manager import LoggerManager


SYNC_SECONDS_AGO = 30  # TODO move from here
SYNC_NB_DAYS_NEWS = 7  # TODO move from here
SYNC_NB_DAYS_FINANCE = 7

class SyncManager:

    def __init__(self, app):
        self.app = app
        self.logger = LoggerManager.get_logger(__class__.__name__)


    def sync_client_content(self, client):
        self.logger.debug('sync_client_content')
        if not client:
            return 'client is None'

        error = Error()  # TODO

        with self.app.app_context():
            geoloc = Geoloc.query.get(client.geoloc_id)
            if geoloc:
                if geoloc.category == CATEGORY_NEIGHBORHOOD:  # TODO refactor how to manage sync for geoloc children/parent...
                    geoloc = geoloc.parent
                # end if geoloc.category == CATEGORY_NEIGHBORHOOD
            else:
                error.add("Cannot sync new client if geoloc is unknown. Will sync later on location update")
                return error  # TODO Maybe just send global notification...
            # end if geoloc

            utc_now = dt.datetime.utcnow()
            status_usable_id = Status.query.filter_by(name='usable').one().id
            workflow_published_id = Workflow.query.filter_by(name='published').one().id
            try:
                # News feed includes bulletin and notices
                self._sync_news(client, geoloc, utc_now, status_usable_id, workflow_published_id, error)
                # Finance feed is for prices
                self._sync_finance(client, geoloc, utc_now, status_usable_id, workflow_published_id, error)
            except Exception as e:
                self.logger.warning('Exception while SYNCing: {}'.format(e))  # TODO exception
        # TODO sync for !!!!!!!!!!!!
        # admin
        # static
        # notice
        # report
        # other1
        # Advice
        # other2
        return error


    def _sync_news(self, client, geoloc, utc_now, status_id, workflow_id, error):
        self.logger.debug('_sync_news')
        sync_limit_time = utc_now - timedelta(seconds=SYNC_SECONDS_AGO)  # TODO magic number
        self.logger.debug('SYNC News starting for client client_id/id {}/{}, geoloc_id: {}, client.synced_news: {}, sync_limit_time: {}'
                          .format(client.device_id, client.id, geoloc.id, client.synced_news, sync_limit_time))
        if geoloc and client and client.synced_news and client.synced_news < sync_limit_time:  # TODO magic number
            if geoloc.category == CATEGORY_NEIGHBORHOOD:
                geoloc = geoloc.parent
            # end if geoloc.category == CATEGORY_NEIGHBORHOOD
            item_list = {}

            sync_n_days = utc_now - timedelta(days=SYNC_NB_DAYS_NEWS)  # TODO magic number

            geoloc_tmp = geoloc
            while geoloc_tmp:
                item_array = FeedNews.query.filter(db.and_(db.func.date(FeedNews.updated) >= sync_n_days,
                                                           FeedNews.geoloc_list.contains(geoloc_tmp),
                                                           FeedNews.status_id == status_id,
                                                           FeedNews.workflow_id == workflow_id)).all()
                if item_array:
                    item_list.update({geoloc_tmp: item_array})
                # end if item_array
                geoloc_tmp = geoloc_tmp.parent
            # end while geoloc_tmp

            for child in geoloc.child_list:
                item_array = FeedNews.query.filter(db.and_(db.func.date(FeedNews.updated) >= sync_n_days,
                                                           FeedNews.geoloc_list.contains(child),
                                                           FeedNews.status_id == status_id,
                                                           FeedNews.workflow_id == workflow_id)).all()
                if item_array:
                    item_list.update({child: item_array})
                # end for for child in geoloc.child_list
            # end for child in geoloc.child_list

            self.logger.debug('SYNC News for client device_id/client_id {}/{}, geoloc_id: {}, item_list: {}'
                              .format(client.device_id, client.id, geoloc.id, str(item_list)))
            if item_list:
                nb_updates = 0
                for geoloc_item, item_array in item_list.items():
                    for item in item_array:
                        self._sync_news_for_client(item, client, geoloc_item, error)
                        if not error:
                            nb_updates += 1
                        # end if not error
                    # end for item in item_array
                # end for geoloc_item, item_array in item_list.items()

                if not error and nb_updates > 0:
                    client.synced_news = utc_now
                    client.save()
                    db.session.commit()
                    # End for bulletin
                    # TODO log
                    self.logger.debug('SYNC News done for client device_id/client_id: {}/{}, nb_updates: {}'.format(client.device_id, client.id, nb_updates))

                if error:
                    self.logger.warnung('SYNC News ERROR for client device_id/client_id: {}/{}, error: {}'.format(client.device_id, client.id, error.msg()))
                # end if not error and nb_updates > 0
            # end if item_list
        else:
            self.logger.debug("No SYNC News for client.synced_news: {}, sync_limit_time: {}".format(client.synced_news, sync_limit_time))
            # end if client.synced_news and utc_now - client.synced_news > timedelta(hours=1)


    def _sync_news_for_client(self, news, client, geoloc, error: Error):
        self.logger.debug('_sync_news_for_client')
        # TODO consolidate with below _sync_prices_for_client
        if news:
            self.logger.debug('SYNC News client.device_id: {}, client.id: {}, geoloc.id: {}, news.id: {}'
                              .format(client.device_id, client.id, geoloc.id, news.id))
            try:
                json_dict = news.to_dict_one_geoloc(geoloc)
                if json_dict:  # should not be none ever except if there is a code issue
                    json_dict.update({'device_id': client.device_id, 'command': 'sync'})
                    # profile_id_b = int(news.profile_id).to_bytes(4, byteorder='little', signed=True)
                    # item_id_b = int(news.id).to_bytes(8, byteorder='little', signed=True)
                    _, err = self.app.forwarder.send_data_sync(json.dumps(json_dict).encode())
                    if err:
                        error.add(err)
                    # end if err
                # end if json_dict
            except Exception as e:
                error.add('{}\n'.format(str(e)))  # TODO exception
                # TODO log
                self.logger.warning('SYNC News ERROR: {}'.format(error.msg()))


    def _sync_finance(self, client, geoloc, utc_now, status_id, workflow_id, error):
        self.logger.debug('_sync_finance')
        sync_limit_time = utc_now - timedelta(seconds=SYNC_SECONDS_AGO)  # TODO magic number
        self.logger.debug('SYNC Finance starting for client device_id/client_id {}/{}, geoloc_id: {}, category: {}, '
                          'client.synced_finance: {}, sync_limit_time: {}'
                          .format(client.device_id, client.id, geoloc.id, geoloc.category, client.synced_finance, sync_limit_time))
        if geoloc and client and client.synced_finance and client.synced_finance < sync_limit_time:  # TODO magic number
            if geoloc.category == CATEGORY_SUBDISTRICT:  # Finance are set at DISTRICT level
                geoloc = geoloc.parent
            # end if geoloc.category == CATEGORY_DISTRICT
            sync_n_days = utc_now - timedelta(days=SYNC_NB_DAYS_FINANCE)  # TODO magic number
            finance_list = FeedFinance.query \
                .filter(db.and_(db.func.date(FeedFinance.updated) >= sync_n_days,
                                FeedFinance.geoloc_list.contains(geoloc),
                                FeedFinance.status_id == status_id,
                                FeedFinance.workflow_id == workflow_id)).all()
            nb_updates = 0
            if finance_list:
                for finance in finance_list:
                    # TODO revise this, here we publish for the geoloc parent (i.e. district) only
                    if finance.price_list and len(finance.price_list) > 0:
                        self._sync_prices_for_client(finance, client, geoloc, error)
                        if not error:
                            nb_updates += 1
                        # end if not error
                    # end if finance.price_list and len(finance.price_list) > 0
                # End for finance in finance_list
            else:
                self.logger.debug('SYNC Finance device_id/client_id {}/{}, finance_list is empty'.format(client.device_id, client.id))
            # end if finance_list

            if not error and nb_updates > 0:
                client.synced_finance = utc_now
                client.save()
                db.session.commit()
                self.logger.debug('SYNC Finance done for client device_id/client_id: {}/{}, nb_updates: {}'
                                  .format(client.device_id, client.id, nb_updates))

            if error:
                self.logger.warning('SYNC Finance ERROR for client device_id/client_id {}/{}, error: {}'
                                    .format(client.device_id, client.id, error.msg()))


    def _sync_prices_for_client(self, finance, client, geoloc, error):
        self.logger.debug('_sync_prices_for_client')
        # TODO consolidate with above _sync_news_for_client
        if client and geoloc and finance and finance.price_list:
            self.logger.debug('SYNC Finance client.device_id: {}, client.id: {}, geoloc.id: {}, finance.id: {}, finance.version: {}'
                              .format(client.device_id, client.id, geoloc.id, finance.id, finance.version))
            try:
                # Prepare the list of prices as an array of dictionaries
                body_dict_array = [p.to_dict() for p in finance.price_list if p.value is not None]
                # Form the json message from a template
                json_dict = header_as_dict(finance, body_dict_array, geoloc)
                if json_dict:  # should not be none ever except if there is a code issue
                    json_dict.update({'device_id': client.device_id, 'command': 'sync'})
                    # Wrap the message metadata
                    profile_id = finance.profile_id
                    # profile_id_b = int(profile_id).to_bytes(4, byteorder='little', signed=True)
                    # item_id_b = int(finance.id).to_bytes(8, byteorder='little', signed=True)
                    _, err = self.app.forwarder.send_data_sync(json.dumps(json_dict).encode())
                    if err:
                        error.add(err)
                    # end if err
                # end if json_dict
            except Exception as e:
                error.add('{}\n'.format(str(e)))  # TODO exception
                self.logger.warning('SYNC Finance ERROR: {}'.format(error.msg()))
