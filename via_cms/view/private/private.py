#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from flask import Blueprint
from flask import send_from_directory
from flask_login import login_required

from via_cms.util.helper import render_extensions


bp = Blueprint('private', __name__, static_folder="../static")


@bp.route("/private/", methods=["GET", "POST"])
@login_required
def home():
    return render_extensions("private/home.html")


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    # This is used in item details to read the renditions images
    from via_cms.main import get_config_flask
    config_flask = get_config_flask()
    return send_from_directory(config_flask.UPLOADED_FILES_DEST, filename)

