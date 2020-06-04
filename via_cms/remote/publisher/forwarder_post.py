#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from via_common.multiprocess.background_thread import BackgroundThread
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.network.channel import Channel
from via_common.network.middleware_redis import MiddlewareRedis
from via_common.network.source_type import SourceType
from via_common.util.config_mixin_logger import ConfigMixInLogger
from via_common.util.config_mixin_server import ConfigMixInServer
from via_common.util.helper import wrap_message, get_next_cms_id


class ForwarderPost(BackgroundThread):

    def __init__(self, config_middleware: ConfigMixInServer, config_internal_conn: ConfigMixInServer, config_logger: ConfigMixInLogger):
        super().__init__(config_internal_conn, MiddlewareRedis(config_middleware,
                                                               config_logger,
                                                               LoggerManager.logger_queue))
        self.channel = Channel.FROM_CMS


    def start(self):
        self._start_background_async(self._subscribe_forever, (self.channel + 'ACK', self._on_acknowledgement,))


    def _initialise_thread_logger(self):
        self.logger = LoggerManager.get_logger(__class__.__name__)


    def _subscribe_forever(self, channel, callback):
        self.middleware.subscribe_one_forever(channel, callback)


    def shutdown(self):
        # The mechanism uses a pipe to send a 'shutdown' command to each process.
        # The pipe is handled by an orchestrator.
        self.logger.fatal('Shutting down')
        self.middleware.shutdown()


    def _on_acknowledgement(self, message):
        self.logger.debug(message)
        # TODO _on_acknowledgement


    def send_data_sync(self, data: bytes):
        error = ''
        try:
            message_id = get_next_cms_id()
            payload = wrap_message(message_id, SourceType.CMS, data)
        except Exception as e:
            error = 'Wrapping failed: {}'.format(e)
        try:
            self.middleware.publish(Channel.FROM_CMS, payload)
            self.logger.debug('SENT payload ; message_type {}, payload_id {}'.format(SourceType.CMS, message_id))
        except Exception as e:
            error = str(e)
        return message_id, error
