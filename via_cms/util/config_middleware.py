#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#
#

import os

#
#
#

from via_common.util.config_mixin_server import ConfigMixInServer


class ConfigMiddleware(ConfigMixInServer):

    def __init__(self):
        super().__init__('middleware')


    @classmethod
    def get_config_path(cls):
        return os.getenv('VIA_CMS_CONFIG_PATH')


    @classmethod
    def get_config_filename(cls):
        return os.getenv('VIA_CMS_MIDDLEWARE_CONFIG_FILENAME') or 'middleware.json'


    @classmethod
    def _init_config(cls):
        pass
