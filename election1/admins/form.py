from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import Length, Email, InputRequired
from election1.models import Admin_roles
from wtforms_alchemy.fields import QuerySelectField


def admin_roles_query():
    return Admin_roles.query


class UserForm(FlaskForm):
    user_firstname = StringField(label='Firstname', validators=[Length(min=2, max=30), InputRequired()])
    user_lastname = StringField(label='Lastname', validators=[Length(min=2, max=30), InputRequired()])
    user_so_name = StringField(label='User Name', validators=[Length(min=2, max=30), InputRequired()])
    user_pass = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired()])
    # user_role = StringField(label='role',  validators=[Length(min=1, max=1), InputRequired()])
    id_admin_role = QuerySelectField(query_factory=admin_roles_query, label='Admin Role', get_label='admin_role_name')

    user_email = EmailField(label='Email', validators=[Email()])
    submit = SubmitField(label='Submit')



