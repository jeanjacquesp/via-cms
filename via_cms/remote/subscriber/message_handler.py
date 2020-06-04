#  -*- coding: utf-8 -*-
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import datetime as dt
#
#
import json
import traceback

from via_common.multiprocess.logger_manager import LoggerManager
from via_common.network.source_type import SourceType
from via_common.util.error import Error
from via_common.util.helper import deserialize_device_post

from via_cms.model import FeedPost
from via_cms.model.monitor.client_dao import Client
from via_cms.model.monitor.feedback_dao import Feedback
from via_cms.model.static.geoloc_dao import Geoloc
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.subject_dao import Subject


class MessageHandler:
    """
    A callable data handler that transform compressed in-house formatted payload into the json
    format (similar to iptc ninjs) readable by the external receiver (e.g. CMS).
    """


    def __init__(self, app, sync_manager):
        self.app = app
        self.sync_manager = sync_manager
        self.logger = LoggerManager.get_logger(__class__.__name__)


    def __call__(self, mqtt_message):
        return self.handle_payload(mqtt_message)


    def handle_message(self, source_type, payload):
        self.logger.debug('handle_message')
        error = Error()
        try:
            if source_type == SourceType.DEVICE:
                message = deserialize_device_post(payload)
                error += self._handle_device_post(message)
            else:
                return 'Unknown source'
        except Exception as e:
            # TODO Exception
            import traceback
            traceback.print_tb(e.__traceback__)  # TODO
            err_msg = 'handle_message - raise EXCEPTION for message. Source_type: {}, error: {}'.format(source_type, str(e))
            error.add(err_msg)
            # TODO log
        if error:
            self.logger.warning(error.msg())
        return error


    def _handle_device_post(self, device_post):
        error = Error()
        with self.app.app_context():
            if device_post.profile_id == Profile.query.filter_by(name='device').one().id:
                if device_post.subject_id == Subject.query.filter_by(name='new_client').one().id:  # 'new_client':   TODO magic
                    error += self._handle_new_client(device_post)
                elif device_post.subject_id == Subject.query.filter_by(name='feedback').one().id:  # 'feedback':    TODO magic
                    error += self._handle_feedback(device_post)
                elif device_post.subject_id == Subject.query.filter_by(name='location_change').one().id:  # 'location_change':   TODO magic
                    error += self._handle_location_change(device_post)
                else:  # todo unknown profile
                    err_msg = 'handle_message - UNKNOWN profile for input message {}/{}'.format(packet_type, packet_id)
                    error.add(err_msg)
            else:  # todo unknown profile
                err_msg = 'handle_message - UNKNOWN profile for input message {}/{}'.format(packet_type, packet_id)
                error.add(err_msg)

        return error


    def _handle_feedback(self, device_post):
        self.logger.debug('_handle_feedback')
        error = Error()
        with self.app.app_context():
            device_id = device_post.device_id
            item_id = device_post.feedback.item_id
            item_version = device_post.feedback.item_version
            try:
                feedback_json = json.dumps(device_post.feedback.feedback_json)
            except Exception as e:
                traceback.print_tb(e.__traceback__)  # TODO
                error.add('json error: {}'.format(str(e)))
            post = FeedPost.query.get((item_id, item_version))
            if not post:
                error.add('Post unknown for id: {}, version: {}'.format(item_id, item_version))
            else:
                client = Client.query.filter_by(device_id=device_id).first()  # TODO error prone
                if client:
                    feedback = Feedback(client_id=client.id, client=client, post_id=item_id, post=post,
                                        feedback_json=feedback_json)
                    feedback.save()
                    if post:
                        post.feedback_list.append(feedback)
                        post.save()
                    client.feedback_list.append(feedback)
                    client.save()
                    client_fdb_json = ""
                    try:
                        client_fdb_json = str(device_post.feedback.feedback_json)
                    except:  # TODO properly
                        error.add('Error while handling feedback for client id, item_id, feedback: {}, {}, {}. No feedback found'
                                  .format(client.id, item_id, client_fdb_json))
                    else:
                        self.logger.info('Handle feedback for client id, item_id, feedback: {}, {}, {}'.format(client.id, item_id, client_fdb_json))
                else:
                    error.add('client unknown')
                # End if client
            # end if not post
        # End with self.app.app_context()
        return error


    def _handle_new_client(self, device_post):
        self.logger.debug('_handle_new_client')
        error = Error()
        with self.app.app_context():
            device_id = device_post.device_id
            geoloc_id = device_post.geoloc_id
            try:
                geoloc_id = int(geoloc_id)
            except ValueError as e:
                error.add('Invalid geoloc_id string {} for device id: {}'.format(geoloc_id, device_id))
                self.logger.warning(error.msg())
                return error
            geoloc = Geoloc.query.get(geoloc_id)
            if not geoloc:
                # It is ok not to have geoloc as the device gps might not have got the geoloc yet.
                error.add('Unknown geoloc {} for device id: {}'.format(geoloc_id, device_id))
                self.logger.warning(error.msg())
                # TODO this is temporary. the issue is that mysql does not accept a geoloc that does not exist, obviously
                geoloc_id = 1000
            # end if not geoloc
            client = Client.query.filter_by(device_id=device_id).first()
            # The client should be new
            if not client:
                client = Client(device_id=device_id, geoloc_id=geoloc_id)
                client.save()
            else:
                error.add('client already registered, device_id: {}, geoloc_id: {}'.format(device_id.geoloc_id))

            if not error:
                self.logger.info('Handle new client id: {}, device_id: {}'.format(client.id, device_id))
            error += self.sync_manager.sync_client_content(client)
        # End with self.app.app_context()

        return error


    def _handle_location_change(self, device_post):
        self.logger.debug('_handle_location_change')
        error = Error()
        with self.app.app_context():
            device_id = device_post.device_id
            geoloc_id = device_post.geoloc_id
            try:
                geoloc_id = int(geoloc_id)
            except ValueError as e:
                error.add('Invalid geoloc_id string {} for device id: {}'.format(geoloc_id, device_id))
                self.logger.warning(error.msg())
                return error
            geoloc = Geoloc.query.get(geoloc_id)
            if not geoloc:
                error.add('Unknown geoloc {} for device id: {}'.format(geoloc_id, device_id))
                self.logger.warning(error.msg())
                return error
            client = Client.query.filter_by(device_id=device_id).first()
            # The client should exist already
            if client:
                client.geoloc_id = geoloc_id
                client.updated = dt.datetime.utcnow()
                client.save()
            else:
                # it is an error but we should then create it anyway
                error += self._handle_new_client(device_post)
                if error:
                    return error
                # end if error
                client = Client.query.filter_by(device_id=device_id).first()
            # end if client

            self.logger.info('Handle location change client id, geoloc_id: {}, {}'.format(client.id if client else 'Unknown', geoloc_id))
            error += self.sync_manager.sync_client_content(client)
        # End with self.app.app_context()

        return error
