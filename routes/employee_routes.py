from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from models import db, Employee
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime


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
        user_data = db.session.execute(db.select(Employee)).scalars().all()
        employee_dict = [
            {
                "employee_id": data.employee_id,
                "first_name": data.first_name,
                "middle_name": data.middle_name,
                "last_name": data.last_name,
                "address": data.address,
                "email": data.email,
                "phone": data.phone,
                "hire_date": data.hire_date,
                "is_active": data.is_active,
                "email_confirm": data.email_confirm,
            } for data in user_data]
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
        employee_data = db.session.query(Employee).filter_by(employee_id=employee_id).first()
        if employee_data:
            employee_dict = {
                "employee_id": employee_data.employee_id,
                "first_name": employee_data.first_name,
                "middle_name": employee_data.middle_name,
                "last_name": employee_data.last_name,
                "address": employee_data.address,
                "email": employee_data.email,
                "phone": employee_data.phone,
                "hire_date": employee_data.hire_date,
                "is_active": employee_data.is_active,
                "email_confirm": employee_data.email_confirm,
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

            recipient_email = request.form.get("email")
            token = s.dumps(recipient_email, salt='email-confirm')

            subject = 'Confirm Email'
            body = f"Click the following link to confirm your email: {BASE_URL}/employee/confirm-email/{token}"

            msg = MIMEText(body)
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

            new_employee = Employee(
                first_name=request.form.get("first_name"),
                middle_name=request.form.get("middle_name"),
                last_name=request.form.get("last_name"),
                address=request.form.get("address"),
                email=request.form.get("email"),
                password=pbkdf2_sha256.hash(request.form.get("password")),
                phone=request.form.get("phone"),
                position=request.form.get("position"),
                hire_date=datetime.strptime(request.form.get("hire_date"), '%Y-%m-%d').date()
            )

            db.session.add(new_employee)
            db.session.commit()

            new_employee_dict = [
                {
                    "employee_id": new_employee.employee_id,
                    "first_name": new_employee.first_name,
                    "middle_name": new_employee.middle_name,
                    "last_name": new_employee.last_name,
                    "address": new_employee.address,
                    "email": new_employee.email,
                    "phone": new_employee.phone,
                    "hire_date": new_employee.hire_date,
                    "is_active": new_employee.is_active,
                    "email_confirm": new_employee.email_confirm,
                }
            ]

            return jsonify(
                success={"message": "Employee need to confirm the email.", "employee": new_employee_dict}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to register a new employee. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


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
                return jsonify(success={"message": "email and password are match."}), 200

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
            send_reset_email(email, reset_token)

            return jsonify(success={"message": "Reset link sent to your email. Check your inbox."}), 200

        except Exception as e:
            return jsonify(error={"message": f"Failed to reset password. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


def send_reset_email(email, reset_token):
    subject = 'Password Reset'
    body = (f"Click the following link to reset your password: "
            f"http://127.0.0.1:5013/employee/reset-password/{reset_token}")

    msg = MIMEText(body)
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
    try:

        email = s.loads(token, salt='password-reset', max_age=1800)

        # Find the employee with the confirmed email
        employee = Employee.query.filter_by(email=email).first()

        if employee:
            if request.method == 'GET':
                return render_template("reset_password.html")

            employee.password = pbkdf2_sha256.hash(request.form["new_password"])
            db.session.commit()

            return '<h1>Change Password Successfully!</h1>'
        else:
            return jsonify(error={"Message": "Email not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


@employee_api.delete("/employee/<int:employee_id>")
def delete_employee_data(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        employee_to_delete = db.session.execute(db.select(Employee).where(Employee.employee_id == employee_id)).scalar()
        if employee_to_delete:
            db.session.delete(employee_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted the employee."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@employee_api.patch('/employee/<int:employee_id>')
def update_employee(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            employee_to_update = Employee.query.filter_by(employee_id=employee_id).first()

            if employee_to_update:
                # Get the fields to update from the form data
                update_data = {'first_name': request.form.get('first_name', employee_to_update.first_name),
                               'middle_name': request.form.get('middle_name', employee_to_update.middle_name),
                               'last_name': request.form.get('last_name', employee_to_update.last_name),
                               'address': request.form.get('address', employee_to_update.address),
                               'phone': request.form.get('phone', employee_to_update.phone),
                               'is_active': True if request.form.get('is_active', '').lower() == 'true' else False,
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
                    setattr(employee_to_update, key, value)

                db.session.commit()

                updated_employee_data = {
                    "employee_id": employee_to_update.employee_id,
                    "first_name": employee_to_update.first_name,
                    "middle_name": employee_to_update.middle_name,
                    "last_name": employee_to_update.last_name,
                    "address": employee_to_update.address,
                    "email": employee_to_update.email,
                    "phone": employee_to_update.phone,
                    "hire_date": employee_to_update.hire_date,
                    "is_active": employee_to_update.is_active,
                    "email_confirm": employee_to_update.email_confirm,
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
