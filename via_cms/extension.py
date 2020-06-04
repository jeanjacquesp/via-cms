#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

"""Extensions module. Each extension is initialized in the app factory located
in main.py
"""

from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()

login_manager = LoginManager()

db = SQLAlchemy()

migrate = Migrate()

debug_toolbar = DebugToolbarExtension()  # TODO TO REMOVE

babel = Babel()
