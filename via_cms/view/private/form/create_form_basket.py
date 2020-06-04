#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileRequired
from wtforms import FileField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional

from via_cms.model.static.profile_dao import Profile
from via_cms.model.static.subject_dao import Subject
from via_cms.util.helper import get_locale


class CreateFormBasket(FlaskForm):
    # status = db.Column(db.Integer)  # 5
    # language = SelectField(_l('Basket language'), choices=[(k, v) for k, v in Config.LANGUAGE_DICT.items()])

    subject = SelectField('Subject', validators=[DataRequired()])

    # geotag_list = TextAreaField(_l('List of Locations'), render_kw={'rows': '1'}, validators=[DataRequired()])
    rendition_thumbnail = FileField(_l('Icon file<p><small>The icon should be square, ideally 40x40 or 80x80 pixels. '
                                       'The image should be optimised for the web (minimal size). It\'s resolution should be 72 ppi '
                                       '(96 ppi if needed) Max size is 2kb. Format supported are jpeg and png</small></p>'), default='',
                                    validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'],
                                                                        _l('Only images of type jpeg or png can be used'))])

    # currency = SelectField('Currency', choices=[('syr','SYR'),], validators=[DataRequired()])
    label_ar = TextAreaField(_l('Label in arabic <small>(required)</small>'), render_kw={'rows': '1', 'placeholder': ''},
                             validators=[DataRequired(), Length(max=128)])
    label_en = TextAreaField(_l('Label in english  <small>(required)</small>'), render_kw={'rows': '1', 'placeholder': ''},
                             validators=[DataRequired(), Length(max=128)])
    unit = TextAreaField(_l('Unit <small>(required)</small>'), render_kw={'rows': '1', 'placeholder': ''},
                         validators=[DataRequired(), Length(max=6)])
    description_ar = TextAreaField(_l('Description in arabic'), render_kw={'rows': '1', 'placeholder': ''},
                                   validators=[Optional(), Length(max=512)])
    description_en = TextAreaField(_l('Description in english'), render_kw={'rows': '1', 'placeholder': ''},
                                   validators=[Optional(), Length(max=512)])

    submit = SubmitField(_l('Submit'))


    def __init__(self):
        super().__init__()
        basket_profile_id = Profile.query.filter_by(name='price').one().id
        lang = get_locale()
        if lang == 'ar':
            self.subject.choices = [(c.name, c.label_ar) for c in
                                    Subject.query.filter_by(profile_id=basket_profile_id)]
        elif lang == 'en':
            self.subject.choices = [(c.name, c.label_en) for c in
                                    Subject.query.filter_by(profile_id=basket_profile_id)]


    def validate(self):
        #: additional validation
        initial_validation = super().validate()
        if not initial_validation:
            return False
        # TODO

        return True
