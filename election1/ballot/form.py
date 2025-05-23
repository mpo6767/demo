from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, ValidationError
from election1.models import BallotType


class BallotTypeForm(FlaskForm):

    @staticmethod
    def validate_ballot_type_name(form, field):
        ballot_type_name = BallotType.query.filter_by(ballot_type_name=field.data).first()
        if ballot_type_name:
            raise ValidationError('ballot_type_name must be unique')

    ballot_type_name = StringField(label='Ballot Type. . .', validators=[Length(min=2, max=45), DataRequired()])
    submit = SubmitField(label='submit')

