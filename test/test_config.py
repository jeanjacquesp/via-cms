#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#



from via_cms.main import create_app
from via_cms.config_flask import ConfigProd, ConfigDevLocal


def test_production_config():
    app = create_app(ConfigProd)
    assert app.config['ENV'] == 'prod'
    assert app.config['DEBUG'] is False
    assert app.config['DEBUG_TB_ENABLED'] is False
    assert app.config['ASSETS_DEBUG'] is False


def test_dev_config():
    app = create_app(ConfigDevLocal)
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG'] is True
    assert app.config['ASSETS_DEBUG'] is True
