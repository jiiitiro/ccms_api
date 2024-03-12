from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from models import db, Customer
from itsdangerous import URLSafeTimedSerializer


customer_api = Blueprint('customer_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')

# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")

s = URLSafeTimedSerializer('Thisisasecret!')


# customer
# get all customer table data
@customer_api.get("/customer/all")
def get_all_customer_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        user_data = db.session.execute(db.select(Customer)).scalars().all()
        customer_dict = [
            {
                "customer_id": data.customer_id,
                "first_name": data.first_name,
                "middle_name": data.middle_name,
                "last_name": data.last_name,
                "address": data.address,
                "email": data.email,
                "phone": data.phone,
                "is_active": data.is_active,
                "email_confirm": data.email_confirm,
            } for data in user_data]
        response = jsonify({"customers": customer_dict})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# get specific customer data
@customer_api.get("/customer/<int:customer_id>")
def get_specific_customer_data(customer_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        customer_data = db.session.query(Customer).filter_by(customer_id=customer_id).first()
        if customer_data:
            customer_dict = {
                "customer_id": customer_data.customer_id,
                "first_name": customer_data.first_name,
                "middle_name": customer_data.middle_name,
                "last_name": customer_data.last_name,
                "address": customer_data.address,
                "email": customer_data.email,
                "phone": customer_data.phone,
                "is_active": customer_data.is_active,
                "email_confirm": customer_data.email_confirm,
            }
            response = jsonify({"customer": customer_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Customer not found"}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


# register new customer
@customer_api.post("/customer/register")
def register_customer():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:

            # Check if the email already exists
            existing_customer = Customer.query.filter_by(email=request.form.get("email")).first()

            if existing_customer:
                return jsonify(error={"message": "Email already exists. Please use a different email address."}), 400

            recipient_email = request.form.get("email")
            token = s.dumps(recipient_email, salt='email-confirm')

            subject = 'Confirm Email'
            body = f"Click the following link to confirm your email: {BASE_URL}/customer/confirm-email/{token}"

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

            new_customer = Customer(
                first_name=request.form.get("first_name"),
                middle_name=request.form.get("middle_name"),
                last_name=request.form.get("last_name"),
                address=request.form.get("address"),
                email=request.form.get("email"),
                password=pbkdf2_sha256.hash(request.form.get("password")),
                phone=request.form.get("phone"),
            )
            db.session.add(new_customer)
            db.session.commit()

            new_customer_dict = [
                {
                    "customer_id": new_customer.customer_id,
                    "first_name": new_customer.first_name,
                    "middle_name": new_customer.middle_name,
                    "last_name": new_customer.last_name,
                    "address": new_customer.address,
                    "email": new_customer.email,
                    "phone": new_customer.phone,
                    "is_active": new_customer.is_active,
                    "email_confirm": new_customer.email_confirm,
                }
            ]

            return jsonify(
                success={"message": "Customer need to confirm the email.", "customer": new_customer_dict}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to register a new customer. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# email confirmation
@customer_api.get("/customer/confirm-email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=1800)

        # Find the customer with the confirmed email
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            # Update the email_confirm status to True
            customer.email_confirm = True
            db.session.commit()

            return '<h1>Email Confirm Successfully!</h1>'
        else:
            return jsonify(error={"Message": "Customer not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


# login customer
@customer_api.post("/customer/login")
def login_customer():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            customer = Customer.query.filter(Customer.email == request.form.get("email")).first()

            if not customer:
                return jsonify(error={"message": "Email doesn't exists in the database. "
                                                 "Please use a registered email address."}), 400

            if not customer.email_confirm:
                return jsonify(error={"message": "Confirm your email before logging in."}), 401

            if not customer.is_active:
                return jsonify(error={"message": "Account has been deactivated. Please email as at "
                                                 "www.busyhands_cleaningservices@gmail.com"}), 401

            if customer and pbkdf2_sha256.verify(request.form.get("password"), customer.password):
                # access_token = create_access_token(identity=customer.customer_id)
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
            server.login(MY_EMAIL,MY_PASSWORD)
            server.sendmail(MY_EMAIL, [receiver_email], msg.as_string())

        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification. Error: {str(e)}")


@customer_api.post("/customer/reset-password")
def customer_forgot_password():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            email = request.form.get("email")
            existing_customer = Customer.query.filter_by(email=email).first()

            if not existing_customer:
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
            f"{BASE_URL}/customer/reset-password/{reset_token}")

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


@customer_api.route("/customer/reset-password/<token>", methods=['GET', 'POST'])
def customer_link_forgot_password(token):
    try:

        email = s.loads(token, salt='password-reset', max_age=1800)

        # Find the customer with the confirmed email
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if request.method == 'GET':
                return render_template("reset_password.html")

            customer.password = pbkdf2_sha256.hash(request.form["new_password"])
            db.session.commit()

            return '<h1>Change Password Successfully!</h1>'
        else:
            return jsonify(error={"Message": "Email not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


@customer_api.delete("/customer/<int:customer_id>")
def delete_customer_data(customer_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        customer_to_delete = db.session.execute(db.select(Customer).where(Customer.customer_id == customer_id)).scalar()
        if customer_to_delete:
            db.session.delete(customer_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted the customer."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@customer_api.patch('/customer/<int:customer_id>')
def update_customer(customer_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            customer_to_update = Customer.query.filter_by(customer_id=customer_id).first()

            if customer_to_update:
                # Get the fields to update from the form data
                update_data = {'first_name': request.form.get('first_name', customer_to_update.first_name),
                               'middle_name': request.form.get('middle_name', customer_to_update.middle_name),
                               'last_name': request.form.get('last_name', customer_to_update.last_name),
                               'address': request.form.get('address', customer_to_update.address),
                               'phone': request.form.get('phone', customer_to_update.phone)}

                # Update the customer fields
                for key, value in update_data.items():
                    setattr(customer_to_update, key, value)

                db.session.commit()

                updated_customer_data = {
                    "customer_id": customer_to_update.customer_id,
                    "first_name": customer_to_update.first_name,
                    "middle_name": customer_to_update.middle_name,
                    "last_name": customer_to_update.last_name,
                    "address": customer_to_update.address,
                    "email": customer_to_update.email,
                    "phone": customer_to_update.phone,
                    "is_active": customer_to_update.is_active,
                    "email_confirm": customer_to_update.email_confirm,
                }

                return jsonify(success={"message": "Customer data updated successfully",
                                        "customer_data": updated_customer_data}), 200
            else:
                return jsonify(error={"message": "Customer not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update customer data. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@customer_api.put("/customer/change-password/<int:customer_id>")
def user_change_password(customer_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Assuming you have a CustomerLogin model
            customer_to_change_pass = Customer.query.filter_by(customer_id=customer_id).first()

            if customer_to_change_pass:

                # Validate old password
                old_password = request.form.get("old_password")
                if old_password and not pbkdf2_sha256.verify(old_password, customer_to_change_pass.password):
                    return jsonify(error={"message": "Incorrect old password."}), 400

                # Update the password if a new password is provided
                new_password = request.form.get("new_password")
                if new_password:
                    customer_to_change_pass.password = pbkdf2_sha256.hash(new_password)

                # Commit the changes to the database
                db.session.commit()

                return jsonify(success={"message": "Successfully change the password."}), 200
            else:
                return jsonify(error={"message": "User not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update customer password. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


