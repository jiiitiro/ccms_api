from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from forms import ChangePasswordForm
from models import Employee, Schedule, Attendance
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from db import db


employee_api = Blueprint('employee_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')

# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")

s = URLSafeTimedSerializer('Thisisasecret!')


# employee
# get all employee table data
@employee_api.get("/employee/all")
def get_all_employee_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Query all employees with their associated schedules
        data = db.session.query(Employee, Schedule).outerjoin(Schedule, Employee.employee_id == Schedule.employee_id).all()

        # Extract relevant data for each employee and schedule
        employee_dict = []
        for employee, schedule in data:
            employee_info = {
                "employee_id": employee.employee_id,
                "first_name": employee.first_name,
                "middle_name": employee.middle_name,
                "last_name": employee.last_name,
                "address": employee.address,
                "email": employee.email,
                "phone": employee.phone,
                "hire_date": employee.hire_date,
                "is_active": employee.is_active,
                "email_confirm": employee.email_confirm,
                "position": employee.position,
                "daily_rate": employee.daily_rate,
                "de_minimis": employee.de_minimis,
                "schedule": {
                    "schedule_id": schedule.schedule_id if schedule else None,
                    "start_time": schedule.start_time.strftime(
                        "%H:%M:%S") if schedule and schedule.start_time else None,
                    "end_time": schedule.end_time.strftime("%H:%M:%S") if schedule and schedule.end_time else None,
                    "day_off": schedule.day_off if schedule else None
                }
            }
            employee_dict.append(employee_info)

        # Create the response
        response = jsonify({"employees": employee_dict})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# get specific employee data
@employee_api.get("/employee/<int:employee_id>")
def get_specific_employee_data(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Query the specific employee with their associated schedule
        employee_data = (db.session.query(Employee, Schedule).
                         outerjoin(Schedule, Employee.employee_id == Schedule.employee_id).
                         filter(Employee.employee_id == employee_id).first())

        if employee_data:
            # Extract employee information
            employee, schedule = employee_data
            employee_dict = {
                "employee_id": employee.employee_id,
                "first_name": employee.first_name,
                "middle_name": employee.middle_name,
                "last_name": employee.last_name,
                "address": employee.address,
                "email": employee.email,
                "phone": employee.phone,
                "hire_date": employee.hire_date,
                "is_active": employee.is_active,
                "email_confirm": employee.email_confirm,
                "position": employee.position,
                "daily_rate": employee.daily_rate,
                "de_minimis": employee.de_minimis,
                "schedule": {
                    "schedule_id": schedule.schedule_id if schedule else None,
                    "start_time": schedule.start_time.strftime("%H:%M:%S") if schedule and schedule.start_time else None,
                    "end_time": schedule.end_time.strftime("%H:%M:%S") if schedule and schedule.end_time else None,
                    "day_off": schedule.day_off if schedule else None
                } if schedule else None  # Include schedule information if available
            }
            response = jsonify({"employee": employee_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Employee not found"}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


# register new employee
@employee_api.post("/employee/register")
def register_employee():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:

            # Check if the email already exists
            existing_employee = Employee.query.filter_by(email=request.form.get("email")).first()

            if existing_employee:
                return jsonify(error={"message": "Email already exists. Please use a different email address."}), 400

            new_employee = Employee(
                first_name=request.form.get("first_name"),
                middle_name=request.form.get("middle_name"),
                last_name=request.form.get("last_name"),
                address=request.form.get("address"),
                email=request.form.get("email"),
                password=pbkdf2_sha256.hash(request.form.get("password")),
                phone=request.form.get("phone"),
                position=request.form.get("position"),
                hire_date=datetime.strptime(request.form.get("hire_date"), '%Y-%m-%d').date(),
                daily_rate=float(request.form.get("daily_rate")),
            )

            # Add new employee to the session
            db.session.add(new_employee)
            db.session.commit()

            # Create a new schedule instance
            new_schedule = Schedule(
                employee_id=new_employee.employee_id,
                start_time=datetime.strptime(request.form.get("start_time"), "%H:%M:%S").time(),
                end_time=datetime.strptime(request.form.get("end_time"), "%H:%M:%S").time(),
                day_off=request.form.get("day_off")
            )

            # Add new schedule to the session
            db.session.add(new_schedule)
            db.session.commit()

            # Prepare response data
            new_employee_dict = {
                "employee_id": new_employee.employee_id,
                "first_name": new_employee.first_name,
                "middle_name": new_employee.middle_name,
                "last_name": new_employee.last_name,
                "address": new_employee.address,
                "email": new_employee.email,
                "phone": new_employee.phone,
                "hire_date": new_employee.hire_date.strftime("%Y-%m-%d"),  # Convert to string,
                "position": new_employee.position,
                "daily_rate": new_employee.daily_rate,
                "de_minimis": new_employee.de_minimis,
                "is_active": new_employee.is_active,
                "email_confirm": new_employee.email_confirm,
                "schedule": {
                    "schedule_id": new_schedule.schedule_id,
                    "start_time": new_schedule.start_time.strftime("%H:%M:%S"),
                    "end_time": new_schedule.end_time.strftime("%H:%M:%S"),
                    "day_off": new_schedule.day_off
                }
            }

            recipient_email = request.form.get("email")
            token = s.dumps(recipient_email, salt='email-confirm')

            # Send Email Confirmation to employee's email
            send_email_confirmation(recipient_email, token, new_employee.first_name)

            return jsonify(
                success={"message": "Register Successfully, employee needs to confirm the email.",
                         "employee": new_employee_dict}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to register a new employee. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


def send_email_confirmation(recipient_email, token, firstname):
    subject = 'Confirm Email'
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f7f7f7;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                padding: 40px;
            }}
            h1 {{
                font-size: 24px;
                color: #333;
            }}
            p {{
                font-size: 16px;
                color: #666;
                margin-bottom: 20px;
            }}
            a {{
                color: #007bff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .password {{
                font-size: 20px;
                color: #333;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                font-size: 14px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello {firstname},</h1>
            <p>Confirm your email address by clicking the following link: <a href="{BASE_URL}/employee/confirm-email/{token}">Confirm Email</a></p>

        </div>
        <div class="footer">
            BusyHands Cleaning Services Inc. 2024 | Contact Us: busyhands.cleaningservices@gmail.com
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))  # Set the message type to HTML
    msg['Subject'] = subject
    msg['From'] = MY_EMAIL
    msg['To'] = recipient_email

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MY_EMAIL, MY_PASSWORD)
            server.sendmail(MY_EMAIL, [recipient_email], msg.as_string())

        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification. Error: {str(e)}")


# email confirmation
@employee_api.get("/employee/confirm-email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=1800)

        # Find the employee with the confirmed email
        employee = Employee.query.filter_by(email=email).first()

        if employee:
            # Update the email_confirm status to True
            employee.email_confirm = True
            employee.is_active = True
            db.session.commit()

            return '<h1>Email Confirm Successfully!</h1>'
        else:
            return jsonify(error={"Message": "Employee not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


# login employee
@employee_api.post("/employee/login")
def login_employee():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            employee = Employee.query.filter(Employee.email == request.form.get("email")).first()

            if not employee:
                return jsonify(error={"message": "Email doesn't exists in the database. "
                                                 "Please use a registered email address."}), 400

            if not employee.email_confirm:
                return jsonify(error={"message": "Confirm your email before logging in."}), 401

            if not employee.is_active:
                return jsonify(error={"message": "Account has been deactivated. Please email as at "
                                                 "www.busyhands_cleaningservices.manpower@gmail.com"}), 401

            if employee and pbkdf2_sha256.verify(request.form.get("password"), employee.password):
                # access_token = create_access_token(identity=employee.employee_id)
                # return {"access_token": access_token}
                login_data_dict = {
                    "employee_id": employee.employee_id,
                    "first_name": employee.first_name,
                    "middle_name": employee.middle_name,
                    "last_name": employee.last_name,
                    "email": employee.email,
                    "is_active": employee.is_active,
                    "email_confirm": employee.email_confirm,
                }

                return jsonify(success={"message": f"Welcome {employee.first_name}!",
                                        "user_data": login_data_dict}), 200

            return jsonify(error={"message": "Invalid credentials."}), 401
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to login. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


def send_email_notification(old_email, new_email):
    receiver_email = old_email
    subject = 'Email Change Notification'
    body = (f"Your email has been changed from {old_email} to {new_email}. If you didn't make this change, "
            f"please contact us immediately.")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = MY_EMAIL
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MY_EMAIL, MY_PASSWORD)
            server.sendmail(MY_EMAIL, [receiver_email], msg.as_string())

        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification. Error: {str(e)}")


@employee_api.post("/employee/reset-password")
def employee_forgot_password():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            email = request.form.get("email")
            existing_employee = Employee.query.filter_by(email=email).first()

            if not existing_employee:
                return jsonify(error={"message": "Email not found in the database. "
                                                 "Please use an registered email address."}), 400
            # If email exists, generate a reset token and send a reset email
            # For simplicity, we're using a simple string as the reset token in this example
            reset_token = s.dumps(email, salt='password-reset')

            # Send the reset email
            send_reset_email(email, reset_token, existing_employee.first_name)

            return jsonify(success={"message": "Reset link sent to your email. Check your inbox."}), 200

        except Exception as e:
            return jsonify(error={"message": f"Failed to reset password. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


def send_reset_email(email, reset_token, first_name):
    subject = 'Password Reset'
    body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    padding: 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    padding: 40px;
                }}
                h1 {{
                    font-size: 24px;
                    color: #333;
                }}
                p {{
                    font-size: 16px;
                    color: #666;
                    margin-bottom: 20px;
                }}
                a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .password {{
                    font-size: 20px;
                    color: #333;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    font-size: 14px;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Dear {first_name},</h1>
                <p>Click the following link to reset your password:  <a href="{BASE_URL}/employee/reset-password/{reset_token}">Reset Password</a></p>

            </div>
            <div class="footer">
                BusyHands Cleaning Services Inc. 2024 | Contact Us: busyhands.cleaningservices@gmail.com
            </div>
        </body>
        </html>
        """

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))  # Set the message type to HTML
    msg['Subject'] = subject
    msg['From'] = MY_EMAIL
    msg['To'] = email

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MY_EMAIL, MY_PASSWORD)
            server.sendmail(MY_EMAIL, [email], msg.as_string())

        print("Reset email sent successfully")
    except Exception as e:
        print(f"Failed to send reset email. Error: {str(e)}")


@employee_api.route("/employee/reset-password/<token>", methods=['GET', 'POST'])
def employee_link_forgot_password(token):
    form = ChangePasswordForm()
    try:
        email = s.loads(token, salt='password-reset', max_age=1800)

        user = Employee.query.filter_by(email=email).first()

        if user:
            if form.validate_on_submit():
                user.password = pbkdf2_sha256.hash(form.new_password.data)
                db.session.commit()

                return ('<h1 style="font-family: Arial, sans-serif; font-size: 24px; color: #333; text-align: center; '
                        'margin-top: 50px;">Change Password Successfully!</h1>')
            else:
                return render_template("reset_password.html", form=form)
        else:
            return jsonify(error={"Message": "Email not found."})

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


@employee_api.delete("/employee/<int:employee_id>")
def delete_employee_data(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Find the employee to delete
            employee_to_delete = Employee.query.get(employee_id)
            if not employee_to_delete:
                return jsonify(error={"Not Found": f"Employee with ID {employee_id} not found."}), 404

            # Delete associated attendance records
            Attendance.query.filter_by(employee_id=employee_id).delete()

            # Delete associated schedule
            Schedule.query.filter_by(employee_id=employee_id).delete()

            # Delete the employee
            db.session.delete(employee_to_delete)
            db.session.commit()

            return jsonify(success={"Success": "Successfully deleted the employee and related attendance records."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to delete the employee. Error: {str(e)}"}), 500
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@employee_api.patch('/employee/<int:employee_id>')
def update_employee(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Retrieve employee and schedule information
            employee_to_update = db.session.query(Employee, Schedule).\
                outerjoin(Schedule, Employee.employee_id == Schedule.employee_id).\
                filter(Employee.employee_id == employee_id).first()

            if employee_to_update:
                # Get the fields to update from the form data
                update_data = {
                    'first_name': request.form.get('first_name', employee_to_update[0].first_name),
                    'middle_name': request.form.get('middle_name', employee_to_update[0].middle_name),
                    'last_name': request.form.get('last_name', employee_to_update[0].last_name),
                    'address': request.form.get('address', employee_to_update[0].address),
                    'phone': request.form.get('phone', employee_to_update[0].phone),
                    'de_minimis': float(request.form.get('de_minimis', employee_to_update[0].de_minimis)),
                    'is_active': True if request.form.get('is_active', '').lower() == 'true' else False,
                    'daily_rate': float(request.form.get('daily_rate', employee_to_update[0].daily_rate)),
                }

                hire_date_str = request.form.get("hire_date", "")
                if hire_date_str:
                    # Check if the hire_date string is not empty
                    try:
                        # Attempt to convert the hire_date string to a date
                        update_data['hire_date'] = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        # Handle the case where the date string is not in the expected format
                        return jsonify(error={"message": "Invalid hire date format. Use YYYY-MM-DD"}), 400

                # Update the employee fields
                for key, value in update_data.items():
                    setattr(employee_to_update[0], key, value)

                # Initialize variables
                schedule = None
                new_schedule = None

                # Update or add schedule information
                if employee_to_update[1]:  # Check if schedule information is available
                    schedule = employee_to_update[1]
                    schedule_data = {
                        'start_time': datetime.strptime(str(request.form.get('start_time', schedule.start_time)),
                                                        "%H:%M:%S").time(),
                        'end_time': datetime.strptime(str(request.form.get('end_time', schedule.end_time)),
                                                      "%H:%M:%S").time(),
                        'day_off': request.form.get('day_off', schedule.day_off),
                    }
                    # Update existing schedule or add new schedule
                    if employee_to_update[1]:
                        # Update existing schedule
                        for key, value in schedule_data.items():
                            setattr(schedule, key, value)
                    else:
                        # Create new schedule
                        new_schedule = Schedule(
                            employee_id=employee_to_update[0].employee_id,
                            start_time=schedule_data['start_time'],
                            end_time=schedule_data['end_time'],
                            day_off=schedule_data['day_off']
                        )
                        db.session.add(new_schedule)
                    db.session.commit()

                    schedule = new_schedule if not schedule else schedule

                # Construct updated_employee_data dictionary with the new schedule data
                updated_employee_data = {
                    "employee_id": employee_to_update[0].employee_id,
                    "first_name": employee_to_update[0].first_name,
                    "middle_name": employee_to_update[0].middle_name,
                    "last_name": employee_to_update[0].last_name,
                    "address": employee_to_update[0].address,
                    "email": employee_to_update[0].email,
                    "phone": employee_to_update[0].phone,
                    "hire_date": employee_to_update[0].hire_date,
                    "is_active": employee_to_update[0].is_active,
                    "email_confirm": employee_to_update[0].email_confirm,
                    "daily_rate": employee_to_update[0].daily_rate,
                    'de_minimis': employee_to_update[0].de_minimis,
                    "schedule": {
                        "start_time": schedule.start_time.strftime("%H:%M:%S"),
                        "end_time": schedule.end_time.strftime("%H:%M:%S"),
                        "day_off": schedule.day_off
                    } if schedule else None
                }

                return jsonify(success={"message": "Employee data updated successfully",
                                        "employee_data": updated_employee_data}), 200
            else:
                return jsonify(error={"message": "Employee not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update employee data. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403



@employee_api.put("/employee/change-password/<int:employee_id>")
def user_change_password(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Assuming you have a EmployeeLogin model
            employee_to_change_pass = Employee.query.filter_by(employee_id=employee_id).first()

            if employee_to_change_pass:

                # Validate old password
                old_password = request.form.get("old_password")
                if old_password and not pbkdf2_sha256.verify(old_password, employee_to_change_pass.password):
                    return jsonify(error={"message": "Incorrect old password."}), 400

                # Update the password if a new password is provided
                new_password = request.form.get("new_password")
                if new_password:
                    employee_to_change_pass.password = pbkdf2_sha256.hash(new_password)

                # Commit the changes to the database
                db.session.commit()

                return jsonify(success={"message": "Successfully change the password."}), 200
            else:
                return jsonify(error={"message": "Employee not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update employee password. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403
