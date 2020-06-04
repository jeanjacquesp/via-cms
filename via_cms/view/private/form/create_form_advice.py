#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileRequired
from wtforms import FileField
from wtforms import IntegerField
from wtforms import Label
from wtforms import RadioField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional

from via_cms.config_flask import ConfigFlask
from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale


class CreateFormAdvice(FlaskForm):
    language = SelectField(_l('Language of the post'), choices=[(k, v) for k, v in ConfigFlask.LANGUAGE_DICT.items()])

    subject = Label(_l('Subject'), "")  # This is necessary. It is a hidden field in the form

    headline = TextAreaField(_l('Headline <small>(required)</small>'),
                             render_kw={'rows': '1', 'data-label': _l('Headline'),
                                        'placeholder': _l('Headline')},
                             validators=[DataRequired(), Length(max=80)])

    rendition_main = FileField(_l('Main Media file <small>(required)</small><small><p>The main media should be rectangular (portrait), '
                                  'ideally with a minimum ratio of 1.5 (e.g. 320 x 480 or 680 x 960 pixels). The width can be more than '
                                  '480 or 960 pixels, as images are scrollable vertically. The image should be optimised for the web '
                                  '(minimal size). It\'s resolution should be 72 ppi (96 ppi if needed). The maximum size is 256kb. '
                                  'Format supported are jpg/jpeg and png</small></p>'), default='',
                               validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'],
                                                                       _l('Only images of type jpeg or png can be used'))])

    rendition_thumbnail = FileField(_l('Icon file<p><small>The icon should be square, ideally 40x40 or 80x80 pixels. '
                                       'The image should be optimised for the web (minimal size). It\'s resolution should be 72 ppi '
                                       '(96 ppi if needed) Max size is 2kb. Format supported are jpg and png</small></p>'), default='',
                                    validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'],
                                                                        _l('Only images of type jpeg or png can be used'))])

    caption = TextAreaField(_l('Caption'),
                            render_kw={'rows': '3', 'data-label': _l('Caption'),
                                       'placeholder': _l('Caption')},
                            validators=[Length(max=255)])

    more_info = TextAreaField(_l('URL for More Info <small>(must start with http:// or https://)</small>'), render_kw={'rows': '1'},
                              validators=[Optional(), Length(max=127)])

    body_json = TextAreaField(_l('Body in json format  <small>(required)</small>'), render_kw={
        'rows': '8'}, validators=[DataRequired(), Length(max=2000)])

    feedback_definition = TextAreaField(_l('Feedback as a series of json string'), render_kw={
        'rows': '10'}, validators=[Optional(), Length(max=2000)])

    submit = SubmitField(_l('Submit'))


    def __init__(self, subject_name):
        super().__init__()
        profile_id = Profile.query.filter_by(name='advice').first().id
        lang = get_locale()
        if lang == 'ar':  # TODO add safeguard
            self.subject.text = Subject.query.filter_by(profile_id=profile_id, name=subject_name).one().label_ar
        elif lang == 'en':
            self.subject.text = Subject.query.filter_by(profile_id=profile_id, name=subject_name).one().label_en


    def validate(self):
        #: additional validation
        initial_validation = super().validate()
        if not initial_validation:
            return False
        # TODO

        return True
