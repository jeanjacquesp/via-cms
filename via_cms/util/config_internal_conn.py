#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#
#

import os

#
# Global config as a data class
#

from via_common.util.config_mixin import ConfigMixIn
from via_common.util.config_mixin_server import ConfigMixInServer


class ConfigInternalConn(ConfigMixInServer):

    def __init__(self):
        super().__init__('internal_conn')


    @classmethod
    def get_config_path(cls):
        return os.getenv('VIA_CMS_CONFIG_PATH')


    @classmethod
    def get_config_filename(cls):
        return os.getenv('VIA_CMS_INTERNAL_CONN_CONFIG_FILENAME') or 'internal_conn.json'


    @classmethod
    def _init_config(cls):
        pass

