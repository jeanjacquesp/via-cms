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


class CreateFormNews(FlaskForm):
    language = SelectField(_l('Language of the post'), choices=[(k, v) for k, v in ConfigFlask.LANGUAGE_DICT.items()])

    subject = Label(_l('Subject'), "")

    # For future use. Not displayed for now. It is why it is optional
    subtitle1 = SelectField(_l('Subtitle - top'), choices=[('place', '$location'), ], validators=[Optional()])

    # For future use. Not displayed for now. It is why it is optional
    # subtitle2 = SelectField(_l('Subtitle - bottom'), choices=[('event', '$event_date'), ], validators=[Optional()])

    headline = TextAreaField(_l('Headline <small>(required)</small>'),
                             render_kw={'rows': '1', 'data-label': _l('Headline'), 'placeholder': _l('Headline')},
                             validators=[DataRequired(), Length(max=128)])

    additional_Info = TextAreaField(_l('Additional Information'),
                                    render_kw={'rows': '3', 'data-label': _l('Additional Information'),
                                               'placeholder': _l('Additional Information')},
                                    validators=[Length(max=255)])

    # Job vacancies notice form
    place = TextAreaField(_l('Place'), render_kw={'rows': '1', 'data-label': _l('Place'), 'placeholder': _l('Place')},
                          validators=[Length(max=70)])

    employer = TextAreaField(_l('Employer organization'),
                             render_kw={'rows': '1', 'data-label': _l('Employer organization'), 'placeholder': _l('Employer organization')},
                             validators=[Length(max=70)])

    position = TextAreaField(_l('Position'), render_kw={'rows': '2', 'data-label': _l('Position'), 'placeholder': _l('Position')},
                             validators=[Length(max=255)])

    qualifications = TextAreaField(_l('Qualifications'),
                                   render_kw={'rows': '2', 'data-label': _l('Qualifications'), 'placeholder': _l('Qualifications')},
                                   validators=[Length(max=150)])

    requirements = TextAreaField(_l('Requirements'),
                                 render_kw={'rows': '2', 'data-label': _l('Requirements'), 'placeholder': _l('Requirements')},
                                 validators=[Length(max=150)])

    about_position = TextAreaField(_l('About the Position'),
                                   render_kw={'rows': '3', 'data-label': _l('About the Position'),
                                              'placeholder': _l('About the Position')},
                                   validators=[Length(max=255)])

    # official statements/decisions form
    summary = TextAreaField(_l('Summary'), render_kw={'rows': '2', 'data-label': _l('Summary'), 'placeholder': _l('Summary')},
                            validators=[Length(max=255)])

    date = TextAreaField(_l('Date'), render_kw={'rows': '1', 'data-label': _l('Date'), 'placeholder': _l('23.09.2019')},
                         validators=[Length(max=10)])

    end_date = TextAreaField(_l('End Date (Optional)'), render_kw={'rows': '1', 'placeholder': _l('22.01.2020')},
                             validators=[Length(max=10)])

    # missing persons form
    name = TextAreaField(_l('Name'), render_kw={'rows': '1', 'data-label': _l('Name'), 'placeholder': _l('Name')},
                         validators=[Length(max=70)])

    gender = RadioField(_l('Gender'), choices=[('male', 'Male'), ('female', 'Female')], default='male',
                        render_kw={'data-label': _l('Gender')})

    age = IntegerField(_l('Age'), render_kw={'data-label': _l('Place'), 'placeholder': _l('ex: 13')},
                       validators=[NumberRange(min=1, max=120)], default=10)

    special_marks = TextAreaField(_l('Special Marks'),
                                  render_kw={'rows': '1', 'data-label': _l('Special Marks'), 'placeholder': _l('Special Marks')},
                                  validators=[Length(max=150)])

    # lost item form
    item_type = TextAreaField(_l('Item Type'),
                              render_kw={'rows': '1', 'data-label': _l('Item Type'), 'placeholder': _l('Item Type')},
                              validators=[Length(max=70)])

    description = TextAreaField(_l('Description'),
                                render_kw={'rows': '3', 'data-label': _l('Description'), 'placeholder': _l('Description')},
                                validators=[Length(max=255)])

    # aid distribution form
    aid_type = TextAreaField(_l('Aid Type'),
                             render_kw={'rows': '1', 'data-label': _l('Aid Type'), 'placeholder': _l('Aid Type')},
                             validators=[Length(max=70)])

    aid_details = TextAreaField(_l('Details of assistance provided'),
                                render_kw={'rows': '3', 'data-label': _l('Details of assistance provided'),
                                           'placeholder': _l('Details of assistance provided')},
                                validators=[Length(max=255)])
    # vaccination campaigns form
    vaccination_type = TextAreaField(_l('Vaccination Type'),
                                     render_kw={'rows': '2', 'data-label': _l('Vaccination Type'), 'placeholder': _l('Vaccination Type')},
                                     validators=[Length(max=150)])

    concerned_persons = TextAreaField(_l('Concerned Persons'),
                                      render_kw={'rows': '2', 'data-label': _l('Concerned Persons'),
                                                 'placeholder': _l('Concerned Persons')},
                                      validators=[Length(max=150)])

    vaccination_age = TextAreaField(_l('Age'),
                                    render_kw={'rows': '1', 'data-label': _l('Age'), 'placeholder': _l('Age')},
                                    validators=[Length(max=70)])
    # Events form
    event_type = TextAreaField(_l('Event Type'),
                               render_kw={'rows': '1', 'data-label': _l('Event Type'), 'placeholder': _l('Event type')},
                               validators=[Length(max=70)])

    event_schedule = TextAreaField(_l('Schedule'),
                                   render_kw={'rows': '2', 'data-label': _l('Schedule'), 'placeholder': _l('Schedule')},
                                   validators=[Length(max=150)])

    # ----------------------------------------------------------------------------- #

    body_json = TextAreaField(_l('Body in json format <small>(required)</small>'), render_kw={'rows': '8'},
                              validators=[DataRequired(), Length(max=2000)])

    feedback_definition = TextAreaField(_l('Feedback as a series of json string'),
                                             render_kw={'rows': '10'}, validators=[Optional(), Length(max=2000)])

    more_info = TextAreaField(_l('URL for More Info <small>(must start with http:// or https://)</small>'), render_kw={'rows': '1'},
                              validators=[Optional(), Length(max=127)])

    contact_json = TextAreaField(_l('Contact information as a json string'),
                                 render_kw={'rows': '4'}, validators=[Optional(), Length(max=1000)])

    geotag_list = TextAreaField(_l('List of Locations <small>(required)</small>'), render_kw={'rows': '1'}, validators=[DataRequired()])

    rendition_thumbnail = FileField(_l('Icon file<p><small>The icon should be square, ideally 40x40 or 80x80 pixels. '
                                       'The image should be optimised for the web (minimal size). It\'s resolution should be 72 ppi '
                                       '(96 ppi if needed) Max size is 2kb. Format supported are jpg and png</small></p>'), default='',
                                    validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'],
                                                                        _l('Only images of type jpeg or png can be used'))])

    submit = SubmitField(_l('Submit'))


    def __init__(self, profile_name, subject_name):
        super().__init__()
        subject_name = 'any'
        profile_news_id = Profile.query.filter_by(name='free_form').first().id
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
