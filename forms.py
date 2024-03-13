
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, SelectField
from wtforms.validators import DataRequired, URL, Email, ValidationError, Regexp, Length


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp('^(?=.*[a-zA-Z])(?=.*\d)', message=f'Password must be alphanumeric (contain letters and numbers).')
    ])

    submit = SubmitField("Submit")

