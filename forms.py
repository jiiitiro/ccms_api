
from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import EmailField, StringField
from wtforms.validators import DataRequired, Regexp, Length, Email, EqualTo
from wtforms.widgets import Select


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp('^(?=.*[a-zA-Z])(?=.*\d)', message='Password must be alphanumeric (contain letters and numbers).')
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])

    submit = SubmitField("Submit")


class CustomSelectWidget(Select):
    def __call__(self, field, **kwargs):
        if field.name in kwargs:
            kwargs['id'] = kwargs.pop(field.name)
        html = super().__call__(field, **kwargs)
        return html

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('staff', 'Staff')
    ], validators=[DataRequired()], widget=CustomSelectWidget())
    subsystem = SelectField('Subsystem', choices=[
        ('billing', 'Billing Subsystem'),
        ('customer', 'Customer Subsystem'),
        ('employee', 'Employee Subsystem'),
        ('inventory', 'Inventory Subsystem'),
        ('payroll', 'Payroll Subsystem')
    ], validators=[DataRequired()], widget=CustomSelectWidget())
    submit = SubmitField('Submit')


class ActivateAccount(FlaskForm):
    submit = SubmitField("Activate")


class DeactivateAccount(FlaskForm):
    submit = SubmitField("Deactivate")


class SuperadminLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send")



