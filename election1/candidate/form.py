# Copyright © 2026 Michael O'Connor
# All rights reserved.

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateTimeLocalField, SelectField
from wtforms.validators import Length, DataRequired, ValidationError, InputRequired
from election1.models import Classgrp, Office, Party
from wtforms_alchemy.fields import QuerySelectField


def classgrp_query():
    return Classgrp.query.order_by(Classgrp.sortkey)


def office_query():
    return Office.query.order_by(Office.sortkey)

class CandidateForm(FlaskForm):
    firstname = StringField(label='First Name', validators=[Length(min=2, max=30), InputRequired()])
    lastname = StringField(label='Last Name', validators=[Length(min=2, max=30)])
    choices_classgrp = SelectField('Group', choices=[])
    choices_office = SelectField('Office or Measure', choices=[])
    choices_party = SelectField('Party', choices=[])
    submit = SubmitField(label='Submit')


class Candidate_reportForm(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    submit = SubmitField(label='submit')


class WriteinCandidateForm(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    writein_candidate_name = StringField(label='write-in candidate name', validators=[Length(min=6, max=45), DataRequired()])
    submit = SubmitField(label='submit')

