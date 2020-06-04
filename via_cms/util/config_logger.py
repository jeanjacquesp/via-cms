#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#
#

import os

#
# 
#
from via_common.util.config_mixin_logger import ConfigMixInLogger


class ConfigLogger(ConfigMixInLogger):

    def __init__(self, logger_queue=None):
        super().__init__(logger_queue)

    @classmethod
    def get_config_path(cls):
        return os.getenv('VIA_CMS_CONFIG_PATH')


    @classmethod
    def get_config_filename(cls):
        return os.getenv('VIA_CMS_CONFIG_LOGGER_FILENAME') or 'logger.json'


    @classmethod
    def _init_config_logger(cls, logger_queue):
        pass
