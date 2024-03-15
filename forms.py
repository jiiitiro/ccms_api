
from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp, Length


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp('^(?=.*[a-zA-Z])(?=.*\d)', message=f'Password must be alphanumeric (contain letters and numbers).')
    ])

    submit = SubmitField("Submit")


class ActivateAccount(FlaskForm):
    submit = SubmitField("Activate")


class DeactivateAccount(FlaskForm):
    submit = SubmitField("Deactivate")

