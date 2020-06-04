#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import json
import os
import re
from collections import namedtuple
from functools import wraps

from flask import current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from via_common.multiprocess.logger_manager import LoggerManager
from werkzeug.datastructures import FileStorage

from via_cms.config_flask import ConfigFlask
from via_cms.extension import babel


class Separator:
    FIELD = '®'  # alt 0174
    TAG = '¤'  # alt 0164
    SUB_FIELD = '‡'  # alt 0135
    SUB_TAG = '†'  # alt 0134
    ARRAY_ROW = '§'  # alt 0167
    ARRAY_COLUMN = '»'  # alt 0187
    TEXT_EOL = '¶'  # alt 0182
    TOPIC = '/'
    CSV_COLUMN = ','


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}".format(getattr(form, field).label.text, error), category)
        # end for error in errors
    # end for field, errors in form.errors.items()


def render_extensions(template_path, **kwargs):
    """
    Wraps around the standard render template method and shoves in some other stuff out of the config.
    """
    if 'private' in template_path:
        return render_template(template_path, **kwargs)
    else:
        return render_template(template_path, _GOOGLE_ANALYTICS=current_app.config['GOOGLE_ANALYTICS'], **kwargs)
    # end if 'private' in template_path


def role_required(requirement_list, do_flash=True):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if current_user and current_user.is_allowed(requirement_list):
                return f(*args, **kwargs)
            else:
                error = _l("Only {} have access to this function.".format(', '.join(requirement_list)))
                if do_flash:
                    flash(error, category="warning")
                else:
                    return error
                # End if do_flash
            return redirect(request.referrer)


        # end def wrap(*args, **kwargs)

        return wrap


    # end def decorator(f)

    return decorator


def dao_well_formed(string):
    for c in string:
        if c.isspace() or not (c.isalpha() or c == '_' or c.isdigit()):
            return False
        # end if c.isspace() or not (c.isalpha() or c == '_' or c.isdigit())
    # end for c in string
    return True


def check_json(data, label=''):
    try:
        # data = re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'', data)
        json.loads(data)
    except ValueError as e:
        return '<span class="font-weight-bold">{}</span>'.format(label.capitalize()) + _l(' has json errors: ') + '{}<br>'.format(str(e))
    # end try: json.loads(data)
    return ''


def json2html(json_str):
    html_str = ''
    try:
        if isinstance(json_str, str):
            json_dict = json.loads(json_str)
            if isinstance(json_dict, str):           # TODO temporary fix...
                json_dict = json.loads(json_dict)
        elif not isinstance(json_str, dict):
            return None
        # end if isinstance(json_str, str)
        for k, v in json_dict.items():
            html_str += '<strong>' + k + '</strong>: ' + str(v) + '<br>'
        if not html_str:
            html_str = _l('No data')
        # end for k, v in json_dict.items()
    except json.JSONDecodeError as e:
        return None # TODO exception
    except Exception as e:
        return None  # TODO exception
    return html_str


def _dict2obj(data):
    """
    Helper function for creating the tuple subclasses with well-formed named fields
    """
    return namedtuple('X', (x.replace(' ', '_') for x in data.keys()))(*data.values())


def json2obj(data):
    """
    Deserialize a str or bytes to a Python object using a helper functions to deduce the object
    attributes
    """
    return json.loads(data, object_hook=_dict2obj)


def json2dict(obj):
    """
    Translates a deserialized json object to a dictionary.
    The assumption is that any contained object type has the same class name 'X'.
    """
    res = {}
    for k in obj._fields:
        v = getattr(obj, k)
        if isinstance(v, str):
            res.update({k: v})
        elif isinstance(v, list):
            res2 = []
            for i in v:
                res2.append(json2dict(i))
            res.update({k: res2})
        elif v.__class__.__name__ == obj.__class__.__name__:
            res.update({k: json2dict(v)})
        # if isinstance(v, str)
    # end for k in obj._fields
    return res

def is_rtl():
    direction = ConfigFlask.DIRECTION_DICT.get(get_locale(), 'en')
    if direction == 'rtl':
        return "true"
    # end if direction == 'rtl'
    return "false"


@babel.localeselector
def get_locale():
    if request.args.get("language"):
        session["language"] = request.args.get("language")
    # end if request.args.get("language")
    lang = session.get("language", request.accept_languages.best_match(current_app.config['LANGUAGE_DICT']))
    if lang not in current_app.config['LANGUAGE_DICT']:
        lang = 'ar'
        session["language"] = lang
    # end if lang not in current_app.config['LANGUAGE_DICT']
    return lang


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user:
        return user.timezone
    # end if user is not None


def check_mime_type(rendition: FileStorage):
    rendition_format = ''
    error = ''
    # by default there is no error if the rendition is not set
    if hasattr(rendition, 'filename') and rendition.filename:
        extension = os.path.splitext(rendition.filename)
        if extension and len(extension) > 1:
            extension = extension[-1].lower()
        else:
            error = 'Invalid filename'
        # end if extension and len(extension) > 1
        if extension in ['.jpg', '.jpeg', '.png'] and 'image' in rendition.content_type:  # TODO use flask-uploads
            rendition_format = 'image'
        else:
            if extension not in ['.jpg', '.jpeg', '.png']:
                error = 'File extension "{}" not supported'.format(extension[1:])
            else:
                error = 'Format {} not supported'.format(rendition.content_type)
            # end extension not in ['.jpg', '.jpeg', '.png']
        # end if extension in ['.jpg', '.jpeg', '.png'] and 'image' in rendition.content_type
    # end if hasattr(rendition, 'filename') and rendition.filename
    return rendition_format, error


def check_pwd_complexity(pwd):
    # Very basic password check

    if len(pwd) < 16:
        return 'The password must have at least 16 characters'

    if len(set(pwd)) < 8:
        return 'The password is too simple. Your password must contain at least 8 different characters'

    if pwd.lower() == pwd or pwd.upper() == pwd or pwd.isalnum():
        return 'The password is too simple. Please have at least one upper case and one lower character'

