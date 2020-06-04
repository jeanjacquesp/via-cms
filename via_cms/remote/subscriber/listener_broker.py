#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from via_common.multiprocess.background_thread import BackgroundThread
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.network.channel import Channel
from via_common.network.middleware_redis import MiddlewareRedis
from via_common.network.source_type import SourceType
from via_common.util.config_mixin_logger import ConfigMixInLogger
from via_common.util.config_mixin_server import ConfigMixInServer
from via_common.util.error import Error
from via_common.util.helper import unwrap_payload, wrap_message

from via_cms.device.sync_manager import SyncManager
from via_cms.remote.subscriber.message_handler import MessageHandler


class ListenerBroker(BackgroundThread):

    def __init__(self, config_middleware: ConfigMixInServer, config_internal_conn: ConfigMixInServer, config_logger: ConfigMixInLogger):
        super().__init__(config_internal_conn, MiddlewareRedis(config_middleware,
                                                               config_logger,
                                                               LoggerManager.logger_queue))
        self.channel = Channel.FROM_BROKER
        self.app = None
        self.sync_manager = None
        self.message_handler = None


    def start(self):
        self._start_background_async(self._subscribe_forever, (self.channel, self._on_data_received,))


    def _initialise_thread_logger(self):
        self.logger = LoggerManager.get_logger(__class__.__name__)


    def _subscribe_forever(self, channel, callback):

        self.middleware.subscribe_one_forever(channel, callback)


    def register_app(self, app):
        self.logger.info('Register app')
        self.app = app
        self.sync_manager = SyncManager(app)
        self.message_handler = MessageHandler(app, self.sync_manager)


    def shutdown(self):
        # The mechanism uses a pipe to send a 'shutdown' command to each process.
        # The pipe is handled by an orchestrator.
        self.logger.fatal('Shutting down')
        self.middleware.shutdown()


    def _on_data_received(self, data):
        error = Error()
        if self.app is None:
            error.add('Cannot process data: App is None. Data {}'.format(str(data)))  # TODO manage app is none... need to wait...
            self.logger.warning(error.msg())
            return error
        #
        # read, ack and close
        message_id, source_type, message = unwrap_payload(data)

        #
        # Acknowledge reception, with or without error
        ack = wrap_message(message_id, SourceType.ACK, error.msg().encode() if error else 'ok'.encode())  # TODO ACK

        #
        # Process the message
        if not error:
            self.logger.debug('Handling message received: message_type:{}, message_id:{}'.format(source_type, message_id))
            error += self.message_handler.handle_message(source_type, message)

        if error:
            self.logger.warning(error.msg())
        # End if error
        return error
