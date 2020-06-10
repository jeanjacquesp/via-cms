#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from multiprocessing import freeze_support

from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import lazy_gettext as _l
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.queue_manager import QueueManager

from via_cms import cli
from via_cms.asset import asset
from via_cms.config_flask import ConfigDevLocal
from via_cms.config_flask import ConfigProd
from via_cms.config_flask import ConfigQaTesting
from via_cms.config_flask import ConfigUAT1
from via_cms.extension import babel
from via_cms.extension import bcrypt
from via_cms.extension import db
from via_cms.extension import debug_toolbar
from via_cms.extension import login_manager
from via_cms.extension import migrate
from via_cms.remote.publisher.forwarder_post import ForwarderPost
from via_cms.remote.subscriber.listener_broker import ListenerBroker
from via_cms.util.config_internal_conn import ConfigInternalConn
from via_cms.util.config_logger import ConfigLogger
from via_cms.util.config_middleware import ConfigMiddleware
from via_cms.util.helper import get_locale
from via_cms.view.private import callback
from via_cms.view.private import private
from via_cms.view.private.edition import editor_basket
# from via_cms.view.private.edition import editor_bulletin
from via_cms.view.private.edition import editor_document
from via_cms.view.private.edition import editor_news
# from via_cms.view.private.edition import editor_notice
from via_cms.view.private.edition import editor_price
from via_cms.view.private.user import dashboard_user
from via_cms.view.private.user import detail_user
from via_cms.view.private.user import editor_user
from via_cms.view.private.user import manager_user
from via_cms.view.private.visualization import dashboard_basket
from via_cms.view.private.visualization import dashboard_client
from via_cms.view.private.visualization import dashboard_document
from via_cms.view.private.visualization import dashboard_feedback
from via_cms.view.private.visualization import dashboard_news
from via_cms.view.public import public


"""The app module, containing the app factory function."""

app = None
logger = None
subscriber = None
forwarder = None
listener = None
queue_manager = None
logger = None
config_logger = None
config_internal_conn = None
config_middleware = None
logger_manager = None


def create_app():
    """Flask application factory
    """
    global app
    global logger
    global listener

    if logger:
        logger.warning('Starting Flask')
    else:
        print('Starting Flask')

    config_flask = get_config_flask()

    if not config_flask:
        if logger:
            logger.critical('No config for flask set')
        else:
            print('[CRITICAL] No config for flask set')
        return

    app = Flask(__name__)
    app.config.from_object(config_flask)

    if not os.path.exists(config_flask.DIRECTORY_LOGS):
        os.makedirs(config_flask.DIRECTORY_LOGS)

    if logger:
        app.logger = logger
    else:
        file_handler = RotatingFileHandler(config_flask.DIRECTORY_LOGS + '/via_cms.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                                    '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.DEBUG)
        logger = app.logger

    if not os.path.exists(config_flask.UPLOADED_FILES_DEST):
        # logger.info('Created directory: {}'.format(config_object.UPLOADED_FILES_DEST))
        os.makedirs(config_flask.UPLOADED_FILES_DEST)

    if config_flask == ConfigProd:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

    register_extension(app)
    register_blueprint(app)
    register_error_handler(app)
    cli.command_translate(app)
    cli.command_importer(app)

    app.forwarder = forwarder
    if listener:
        listener.register_app(app)  # TODO redo this listener thing....


    # @app.before_request
    # def before_request():
    #     # if current_user.is_authenticated:
    #     #     current_user.last_seen = dt.datetime.utcnow()
    #     #     db.session.commit()
    #     flask_global.locale = str(get_locale())

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db}


    @app.context_processor
    def language_selector():
        lang = get_locale()
        return {
            "LANGUAGE_DICT": config_flask.LANGUAGE_DICT,
            "CURRENT_LANGUAGE": lang,
            "CURRENT_DIRECTION": config_flask.DIRECTION_DICT.get(lang, 'ltr')
        }


    @app.after_request
    def response_minify(response):
        """
        minify html response
        """
        # if response.content_type == u'text/html; charset=utf-8':
        #     response.set_data(html_minify(response.get_data(as_text=True)))
        #     return response
        return response


    @app.context_processor
    def context_user_manager():
        return dict(user_manager=manager_user)


    # https://stackoverflow.com/questions/30414696/upload-file-larger-than-max-content-length-in-flask-results-connection-reset/49332379#49332379
    @app.errorhandler(Exception)
    def all_exception_handler(error):
        traceback.print_exc()
        logger.error(traceback.extract_tb(error.__traceback__))
        from werkzeug.exceptions import RequestEntityTooLarge
        if isinstance(error, RequestEntityTooLarge):
            message = _l('You attempted to upload a file which is too big. The maximum authorised size is {} kb.<br/>'
                         '<p><small>We had to reset your form to prevent the browser from trying to upload this file.</small></p>'
                         .format(config_flask.MAX_CONTENT_LENGTH / 1024 - 2))
        else:
            message = _l(
                'An unexpected error happened while processing your request. Please contact the IT support. The error is:<br\>{}'
                '<p><small>We had to reset your form to prevent this error from causing further issues.</small></p>'
                    .format(str(error)))
        # end if isinstance(error, RequestEntityTooLarge)
        flash(message, category="error")
        return redirect(url_for(request.endpoint, **request.view_args))


    if logger:
        logger.warning('via_cms INITIALISED')
    return app


def get_config_flask():
    if os.environ.get("VIA_CMS_ENV") == 'prod':
        config_flask = ConfigProd
    elif os.environ.get("VIA_CMS_ENV") == 'uat1':
        config_flask = ConfigUAT1
    elif os.environ.get("VIA_CMS_ENV") == 'dev_local':
        config_flask = ConfigDevLocal
    elif os.environ.get("VIA_CMS_ENV") == 'qa_test':
        config_flask = ConfigQaTesting
    else:
        raise RuntimeError('Environment variable VIA_CMS_ENV not set for config')
    return config_flask


def register_extension(flask_app):
    asset.init_app(flask_app)
    bcrypt.init_app(flask_app)
    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    debug_toolbar.init_app(flask_app)
    migrate.init_app(flask_app, db)
    babel.init_app(flask_app)
    return None


def register_blueprint(flask_app):
    flask_app.register_blueprint(callback.bp)
    flask_app.register_blueprint(dashboard_basket.bp)
    flask_app.register_blueprint(dashboard_client.bp)
    flask_app.register_blueprint(dashboard_document.bp)
    flask_app.register_blueprint(dashboard_feedback.bp)
    flask_app.register_blueprint(dashboard_news.bp)
    flask_app.register_blueprint(dashboard_user.bp)
    flask_app.register_blueprint(detail_user.bp)
    flask_app.register_blueprint(editor_basket.bp)
    flask_app.register_blueprint(editor_document.bp)
    flask_app.register_blueprint(editor_news.bp)
    flask_app.register_blueprint(editor_price.bp)
    flask_app.register_blueprint(editor_user.bp)
    flask_app.register_blueprint(manager_user.bp)
    flask_app.register_blueprint(private.bp)
    flask_app.register_blueprint(public.bp)
    return None


def register_error_handler(flask_app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code


    # end def render_error(error)

    for errcode in [401, 404, 500]:
        flask_app.errorhandler(errcode)(render_error)
    # end for errcode in [401, 404, 500]

    return None


def init_config_logger():
    global config_logger

    if config_logger is None:
        config_logger = ConfigLogger()


def init_config_internal_conn():
    global config_internal_conn

    if config_internal_conn is None:
        config_internal_conn = ConfigInternalConn()


def init_config_middleware():
    global config_middleware

    if config_middleware is None:
        config_middleware = ConfigMiddleware()


def init_logger_manager():
    global logger_manager
    global config_logger

    init_config_internal_conn()
    init_config_logger()
    init_config_middleware()

    if logger_manager is None:
        logger_manager = LoggerManager.init_root_logger(config_logger)


def start_background_tasks():
    global listener
    global forwarder
    global config_internal_conn
    global config_logger
    global config_middleware

    if logger:
        logger.info('Starting background thread')
    config_flask = get_config_flask()

    if config_flask:
        listener = ListenerBroker(config_middleware, config_internal_conn, config_logger)
        listener.start()

        forwarder = ForwarderPost(config_middleware, config_internal_conn, config_logger)  # TODO magic number
        forwarder.start()


def initialise_background():
    global queue_manager
    global logger
    global config_internal_conn
    global config_logger
    global config_middleware

    init_config_internal_conn()
    init_config_logger()
    init_config_middleware()
    init_logger_manager()
    logger = LoggerManager.get_logger('main')
    if logger:
        logger.info('*************************')
        logger.warning('Background initialisation started')
    else:
        print('Logger NOT set for "manager"')
        print('Background initialisation started')
    queue_manager = QueueManager(config_internal_conn)
    start_background_tasks()


def gunicorn_run():
    print('Starting gunicorn_run')  # no logger at this point
    initialise_background()
    if logger:
        logger.info('gunicorn_run')
        logger.warning('Background initialisation done')
    return create_app()


def local_run():
    global app

    print('Starting local_run')
    initialise_background()
    if logger:
        logger.info('local_run')
        logger.info('Background initialisation done')
    config_flask = get_config_flask()
    create_app(config_flask)
    if app:
        app.run()


if __name__ == '__main__':
    freeze_support()
    # this should not be used directly instead you should run through manage.py using the cli
    local_run()
