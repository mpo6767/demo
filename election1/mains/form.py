from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField , PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, ValidationError, InputRequired
from election1.models import Classgrp
from wtforms_alchemy.fields import QuerySelectField


def classgrp_query():
    return Classgrp.query.order_by(Classgrp.sortkey)



class BuildTokensForm(FlaskForm):
    primary_grp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='primary_grp')
    secondary_grp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='secondary_grp')
    tertiary_grp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='tertiary_grp')
    quarternary_grp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='quarternary_grp')
    submit = SubmitField(label='submit')


class LoginForm(FlaskForm):
    login_so_name = StringField(label='Username', validators=[Length(min=2, max=30), InputRequired()])
    login_pass = PasswordField(label='Password', validators=[Length(min=2, max=30), InputRequired()])
    remember = BooleanField(label='remember me')
    submit = SubmitField(label='submit')