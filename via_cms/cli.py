#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import click

from via_cms.model import *


# from via_cms.model._relationship import GeolocPost
# from via_cms.model.feed.basket_dao import Basket
# from via_cms.model.feed.feed_document_dao import FeedDocument
# from via_cms.model.feed.feed_finance_dao import FeedFinance
# from via_cms.model.feed.feed_news_dao import FeedNews
# from via_cms.model.feed.feed_post_dao import FeedPost
# from via_cms.model.feed.price_dao import Price
# from via_cms.model.internal.role_dao import Role
# from via_cms.model.internal.workflow_dao import Workflow
# from via_cms.model.internal.user_dao import User
# from via_cms.model.monitor.client_dao import Client
# from via_cms.model.monitor.feedback_dao import Feedback
# from via_cms.model.static.command_dao import Command
# from via_cms.model.feed.feed_dao import Feed
# from via_cms.model.static.geoloc_dao import Geoloc
# from via_cms.model.static.profile_dao import Profile
# from via_cms.model.static.status_dao import Status
# from via_cms.model.static.subject_dao import Subject
# from via_cms.model.static.widget_dao import Widget


def command_translate(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass


    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        # end if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .')
        if os.system('pybabel init -i messages.pot -d via_cms\translations -l ' + lang):
            raise RuntimeError('init command failed')
        # end if os.system('pybabel init -i messages.pot -d translations -l ' + lang)
        os.remove('messages.pot')


    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        # end if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .')
        if os.system('pybabel update -i messages.pot -d translations'):
            raise RuntimeError('update command failed')
        # end if os.system('pybabel update -i messages.pot -d translations')
        os.remove('messages.pot')


    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d translations'):
            raise RuntimeError('compile command failed')


def command_importer(app):
    @app.cli.group()
    def importer():
        pass


    @importer.command(help='import from csv (UTF-8)')
    @click.argument('file_path')
    @click.argument('table_name')
    def from_csv(file_path, table_name):
        """Import a csv file to the database."""
        if not file_path:
            raise FileExistsError('{} does not exist'.format(file_path))
        # end if not file_path
        if not table_name:
            raise ValueError('Table name should not be empty')
        elif table_name.lower() == 'basket_tbl':
            Basket.import_from_csv(file_path)
        elif table_name.lower() == 'command_tbl':
            Command.import_from_csv(file_path)
        elif table_name.lower() == 'feed_tbl':
            Feed.import_from_csv(file_path)
        elif table_name.lower() == 'widget_tbl':
            Widget.import_from_csv(file_path)
        elif table_name.lower() == 'geoloc_tbl':
            Geoloc.import_from_csv(file_path)
        elif table_name.lower() == 'profile_tbl':
            Profile.import_from_csv(file_path)
        elif table_name.lower() == 'status_tbl':
            Status.import_from_csv(file_path)
        elif table_name.lower() == 'subject_tbl':
            Subject.import_from_csv(file_path)
        elif table_name.lower() == 'role_tbl':
            Role.import_from_csv(file_path)
        elif table_name.lower() == 'user_tbl':
            User.import_from_csv(file_path)
        elif table_name.lower() == 'workflow_tbl':
            Workflow.import_from_csv(file_path)
        else:
            raise ValueError('Table name not part of the CLI.')


    @importer.command(help='export a table to csv (UTF-8)')
    @click.argument('file_path')
    @click.argument('table_name')
    def to_csv(file_path, table_name):
        if not file_path:
            raise FileExistsError('{} does not exist'.format(file_path))
        # end if not file_path
        if not table_name:
            raise ValueError('Table name should not be empty')
        # end if not table_name
        if table_name.lower() == 'geoloc':
            Geoloc.export_to_csv(file_path)
        # end if table_name.lower() == 'geoloc'
