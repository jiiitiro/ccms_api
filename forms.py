
from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Regexp, Length


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp('^(?=.*[a-zA-Z])(?=.*\d)', message='Password must be alphanumeric (contain letters and numbers).')
    ])
    # show_password = BooleanField("Show Password")
    submit = SubmitField("Submit")


class ActivateAccount(FlaskForm):
    submit = SubmitField("Activate")


class DeactivateAccount(FlaskForm):
    submit = SubmitField("Deactivate")

