#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
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


class CreateFormNotice(FlaskForm):
    language = SelectField(_l('Language of the post'), choices=[(k, v) for k, v in ConfigFlask.LANGUAGE_DICT.items()])

    subject = Label(_l('Subject'), "")

    # For future use. Not displayed for now. It is why it is optional
    # subtitle1 = SelectField(_l('Subtitle - top'), choices=[('place', '$location'), ], validators=[Optional()])

    # For future use. Not displayed for now. It is why it is optional
    # subtitle2 = SelectField(_l('Subtitle - bottom'), choices=[('event', '$event_date'), ], validators=[Optional()])

    headline = TextAreaField(_l('Headline'),
                             render_kw={'rows': '1', 'data-label': _l('Headline'), 'placeholder': _l('Headline')},
                             validators=[DataRequired(), Length(max=128)])

    place = TextAreaField(_l('Place'),
                          render_kw={'rows': '1', 'data-label': _l('Place'), 'placeholder': _l('Place')},
                          validators=[Length(max=70)])

    #
    # additional_Info = TextAreaField(_l('Additional Information'),
    #                                 render_kw={'rows': '3', 'data-label': _l('Additional Information'),
    #                                            'placeholder': _l('Additional Information')},
    #                                 validators=[Length(max=255)])

    summary = TextAreaField(_l('Summary'), render_kw={'rows': '2', 'data-label': _l('Summary'), 'placeholder': _l('Summary')},
                            validators=[Length(max=255)])

    date = TextAreaField(_l('Date'), render_kw={'rows': '1', 'data-label': _l('Date'), 'placeholder': _l('23.09.2019')},
                         validators=[Length(max=10)])

    end_date = TextAreaField(_l('End Date (Optional)'), render_kw={'rows': '1', 'placeholder': _l('22.01.2020')},
                             validators=[Length(max=10)])

    # ----------------------------------------------------------------------------- #

    body_json = TextAreaField(_l('Body in json format <small>(required)</small>'), render_kw={'rows': '8'},
                              validators=[DataRequired(), Length(max=2000)])

    feedback_definition = TextAreaField(_l('Feedback as a series of json string'), render_kw={
        'rows': '10'}, validators=[Optional(), Length(max=2000)])

    more_info = TextAreaField(_l('URL for More Info <small>(must start with http:// or https://)</small>'), render_kw={'rows': '1'},
                              validators=[Optional(), Length(max=127)])

    contact_json = TextAreaField(_l('Contact information as a json string'), render_kw={
        'rows': '4'}, validators=[Optional(), Length(max=1000)])

    geotag_list = TextAreaField(_l('List of Locations <small>(required)</small>'), render_kw={'rows': '1'}, validators=[DataRequired()])

    rendition_thumbnail = FileField(_l('Icon file<p><small>The icon should be square, ideally 40x40 or 80x80 pixels. '
                                       'The image should be optimised for the web (minimal size). It\'s resolution should be 72 ppi '
                                       '(96 ppi if needed) Max size is 2kb. Format supported are jpg and png</small></p>'), default='',
                                    validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'],
                                                                        _l('Only images of type jpeg or png can be used'))])

    submit = SubmitField(_l('Submit'))


    def __init__(self, subject_name):
        super().__init__()
        profile_news_id = Profile.query.filter_by(name='notice').first().id
        lang = get_locale()
        if lang == 'ar':  # TODO add safeguard
            self.subject.text = Subject.query.filter_by(profile_id=profile_news_id, name=subject_name).one().label_ar
        elif lang == 'en':
            self.subject.text = Subject.query.filter_by(profile_id=profile_news_id, name=subject_name).one().label_en


    def validate(self):
        #: additional validation
        initial_validation = super().validate()
        if not initial_validation:
            return False
        # TODO

        return True
