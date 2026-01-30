# Copyright © 2026 Michael O'Connor
# All rights reserved.

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import Length, DataRequired



class OfficeForm(FlaskForm):

    office_title = StringField(label='Title', validators=[Length(min=2, max=30), DataRequired()])
    office_vote_for = IntegerField(label='Vote For', default=1)
    sortkey = IntegerField(label='Sort Key', default=None, validators=[DataRequired()])
    ballot_type = SelectField('Ballot Type', choices=[], validators=[DataRequired()])
    office_measure = TextAreaField(label='Measure', validators=[Length(max=256)])
    submit = SubmitField(label='submit')

