#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import os
from multiprocessing.spawn import freeze_support

import click
from flask.cli import FlaskGroup

from via_cms.main import initialise_background
from via_cms.main import create_app
from via_cms.main import start_background_tasks
from via_common.multiprocess.logger_manager import LoggerManager


HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')


@click.group(cls=FlaskGroup, create_app=create_app)
@click.pass_context
def cli(ctx):
    if ctx.parent:
        click.echo(ctx.parent.get_help())


@cli.command(help='run babel')
@click.argument('???')
def BabelCommand():
    capture_all_args = True


    def run(self, args):
        args.insert(0, sys.argv[0])
        from babel.messages.frontend import CommandLineInterface
        cli = CommandLineInterface()
        cli.run(args)


if __name__ == '__main__':
    # This is for manual run using the cli >python manage.py run --no-reload --run-cms
    #   For wsgi run cf. main.py, e.g. gunicorn_run
    freeze_support()
    import sys
    if '--run-cms' in sys.argv:
        sys.argv.remove('--run-cms')
        initialise_background()
        logger = LoggerManager.get_logger('manager')
        if logger:
            logger.warning('Background initialisation done')
            logger.info('manual run')

    # end if '--run-cms' in sys.argv
    cli()
