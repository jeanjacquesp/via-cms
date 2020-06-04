#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import os
from datetime import timedelta
from os import environ
from os import pardir
from os import path


basedir = os.path.abspath(os.path.dirname(__file__))


class ConfigFlask:
    global basedir
    APP_DIR = path.abspath(path.dirname(__file__))  # This directory
    PROJECT_ROOT = path.abspath(path.join(APP_DIR, pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "conn", etc.
    UPLOADED_FILES_DEST = os.path.join(basedir, '../www/upload')
    DIRECTORY_MEDIA_UPLOAD = UPLOADED_FILES_DEST
    MAX_CONTENT_LENGTH = 258 * 1024
    GOOGLE_ANALYTICS = ''
    ERROR_404_HELP = False
    LANGUAGE_DICT = {'ar': 'عربي', 'en': 'English'}
    DIRECTION_DICT = {'ar': 'rtl', 'en': 'ltr'}
    BABEL_DEFAULT_LOCALE = 'ar'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    INSTANCE_PATH = basedir


class ConfigProd(ConfigFlask):
    """Production configuration."""
    pass

class ConfigUAT1(ConfigFlask):
    """Production configuration."""
    pass

class ConfigDevLocal(ConfigFlask):
    """Dev configuration."""
    SECRET_KEY = environ.get('VIA_CMS_SECRET_DEV', 'secret-key')  # TODO: Change me
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the model file in project root
    DB_PATH = path.join(ConfigFlask.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True  # debug toolbar
    ASSETS_DEBUG = True  # Don't bundle/minify static asset
    CACHE_TYPE = 'simple'  # Can be "memcached", "conn", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DIRECTORY_LOGS = os.path.join(basedir, '../log')
    PERMANENT_SESSION = True  # to set flask session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(days=15)  # flask session lifetime
    REMEMBER_COOKIE_DURATION = timedelta(days=1)  # flask-login token's session lifetime


class ConfigQaTesting(ConfigFlask):
    """Test configuration."""
    TESTING = True
    SECRET_KEY = environ.get('VIA_CMS_SECRET_TEST', 'secret-key')  # TODO: Change me
    ENV = 'test'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the model file in project root
    DB_PATH = path.join(ConfigFlask.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = False  # debug toolbar
    ASSETS_DEBUG = False  # Do bundle/minify static asset
    CACHE_TYPE = 'simple'  # Can be "memcached", "conn", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DIRECTORY_LOGS = os.path.join(basedir, '../log')
    PERMANENT_SESSION = True  # to set flask session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(days=15)  # flask session lifetime
    REMEMBER_COOKIE_DURATION = timedelta(days=1)  # flask-login token's session lifetime
