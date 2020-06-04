"""Public section, including homepage and signup."""
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import datetime as dt

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask import url_for
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from via_cms.extension import db
from via_cms.extension import login_manager
from via_cms.model.internal.user_dao import User
from via_cms.util.helper import flash_errors
from via_cms.util.helper import render_extensions
from via_cms.view.private.form.create_form_login import CreateFormLogin


bp = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# @bp.before_request
# def x(*args, **kwargs):
#     if not request.view_args.get('lang_code'):
#         return redirect('/en' + request.full_path)
#
# # @bp.url_defaults
# # def add_language_code(endpoint, values):
# #     if 'lang_code' in values or not hasattr(g,'lang_code'):
# #         values['lang_code'] = None
# #     elif current_app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
# #         values['lang_code'] = g.lang_code
# #
# # @bp.url_value_preprocessor
# # def pull_lang_code(endpoint, values):
# #     g.lang_code = values.pop('lang_code', None)

@bp.route("/", methods=["GET", "POST"])
def home():
    form = CreateFormLogin(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user, duration=current_app.config['REMEMBER_COOKIE_DURATION'])
            if current_user.is_authenticated: # TODO
                current_user.last_seen = dt.datetime.utcnow()
                db.session.commit()
            flash(_l("You are logged in."), category="success")
            redirect_url = request.args.get("next") or url_for("private.home")
            return redirect(redirect_url)
        else:
            flash_errors(form)
        # end if form.validate_on_submit()
    elif request.method == 'GET':
        if current_user and current_user.is_authenticated:
            redirect_url = request.args.get("next") or url_for("private.home")
            return redirect(redirect_url)

    if current_user and current_user.is_authenticated:
        redirect_url = "private/home.html"
    else:
        redirect_url = "public/home.html"

    return render_extensions(redirect_url, form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@bp.route("/about")
def about():
    form = CreateFormLogin(request.form)
    return render_extensions("public/about.html", form=form)


# @bp.route('/robo ts.txt')
@bp.route('/favicon.ico')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None or rule.defaults != '' else ()
    arguments = rule.arguments if rule.arguments is not None or rule.arguments != '' else ()
    return len(defaults) >= len(arguments)


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """
    Generate sitemap.xml. Makes a list of urls and date modified.
    """
    pages = []
    ten_days_ago = dt.datetime.now() - dt.timedelta(days=10)
    ten_days_ago = ten_days_ago.date().isoformat()
    # static pages
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            pages.append([rule.endpoint, url, ten_days_ago])

    sitemap_xml = render_template('public/sitemap_template.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@bp.route('/language_change', methods=['POST'])
def language_picker():
    language = request.get_data()
    language = language.decode('UTF-8')
    session['language'] = language
    return ''  # a 'valid' response is expected, so the an empty str

