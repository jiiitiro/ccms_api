import os
from flask import Blueprint, request, jsonify, render_template
from models import db, InventoryAdminLogin
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
import smtplib
from passlib.hash import pbkdf2_sha256
from app import APP_BASE_URL
BASE_URL = APP_BASE_URL

inventory_admin_api = Blueprint('inventory_admin_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")

s = URLSafeTimedSerializer('Thisisasecret!')


@inventory_admin_api.get("/inventory/admin/all")
def get_all_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        response_data = db.session.execute(db.select(InventoryAdminLogin)).scalars().all()
        user_data = [
            {
                "login_id": data.login_id,
                "name": data.name,
                "email": data.email,
                "role": data.role,
                "is_active": data.is_active,
                "email_confirm": data.email_confirm,
            } for data in response_data
        ]
        response = jsonify({"Admin_Login_Data": user_data})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@inventory_admin_api.get("/inventory/admin/<int:login_id>")
def get_specific_data(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        login_data = db.session.query(InventoryAdminLogin).filter_by(login_id=login_id).first()
        if login_data:
            login_data_dict = {
                "login_id": login_data.login_id,
                "name": login_data.name,
                "email": login_data.email,
                "role": login_data.role,
                "is_active": login_data.is_active,
                "email_confirm": login_data.email_confirm,
            }
            response = jsonify({"login_data": login_data_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Customer not found"}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@inventory_admin_api.post("/inventory/admin/register")
def register():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:

            # Check if the email already exists
            existing_customer = InventoryAdminLogin.query.filter_by(email=request.form.get("email")).first()

            if existing_customer:
                return jsonify(error={"message": "Email already exists. Please use a different email address."}), 400

            recipient_email = request.form.get("email")
            token = s.dumps(recipient_email, salt='email-confirm')

            subject = 'Confirm Email'
            body = (f"Click the following link to confirm your email: "
                    f"{BASE_URL}/inventory/admin/confirm-email/{token}")

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

            new_login = InventoryAdminLogin(
                name=request.form.get("name"),
                email=request.form.get("email"),
                password=pbkdf2_sha256.hash(request.form.get("password")),
                role=request.form.get("role"),
            )

            db.session.add(new_login)
            db.session.commit()

            new_login_dict = [
                {
                    "login_id": new_login.login_id,
                    "name": new_login.name,
                    "email": new_login.email,
                    "role": new_login.role,
                    "is_active": new_login.is_active,
                    "email_confirm": new_login.email_confirm,
                }]

            return jsonify(
                success={"message": f"User need to confirm the email.", "user_data": new_login_dict}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to register. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# Confirm Email
@inventory_admin_api.get("/inventory/admin/confirm-email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=1800)

        # Find the user with the confirmed email
        user = InventoryAdminLogin.query.filter_by(email=email).first()

        if user:
            # Update the email_confirm status to True
            user.email_confirm = True
            user.is_active = True
            db.session.commit()

            return '<h1>Email Confirm Successfully!</h1>'
        else:
            return jsonify(error={"Message": "user not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


@inventory_admin_api.post("/inventory/admin/login")
def login_admin():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            user = InventoryAdminLogin.query.filter(InventoryAdminLogin.email == request.form.get("email")).first()

            if not user:
                return jsonify(error={"message": "Email doesn't exists in the database. "
                                                 "Please use a registered email address."}), 400

            if not user.email_confirm:
                return jsonify(error={"message": "Confirm your email before logging in."}), 401

            if not user.is_active:
                return jsonify(error={"message": "Account has been deactivated. Please email as at "
                                                 "www.busyhands_cleaningservices@gmail.com"}), 401

            if user and pbkdf2_sha256.verify(request.form.get("password"), user.password):
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


@inventory_admin_api.patch("/inventory/admin/<int:login_id>")
def update_user(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            user_to_update = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

            if user_to_update:
                # Get the fields to update from the form data
                update_data = {'name': request.form.get('name', user_to_update.name),
                               'is_active': True if request.form.get('is_active', '').lower() == 'true' else False,
                               'role': request.form.get('role', user_to_update.role)}

                # Update the customer fields
                for key, value in update_data.items():
                    setattr(user_to_update, key, value)

                db.session.commit()

                updated_user_data = {
                    "login_id": user_to_update.login_id,
                    "name": user_to_update.name,
                    "email": user_to_update.email,
                    "role": user_to_update.role,
                    "is_active": user_to_update.is_active,
                    "email_confirm": user_to_update.email_confirm,
                }

                return jsonify(success={"message": "User data updated successfully",
                                        "user_data": updated_user_data}), 200
            else:
                return jsonify(error={"message": "user not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update user data. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@inventory_admin_api.delete("/inventory/admin/<int:login_id>")
def delete_data(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        cust_admin_to_delete = db.session.execute(db.select(InventoryAdminLogin).
                                                  where(InventoryAdminLogin.login_id == login_id)).scalar()
        if cust_admin_to_delete:
            db.session.delete(cust_admin_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted admin login data."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


def send_reset_email(email, reset_token):
    subject = 'Password Reset'
    body = (f"Click the following link to reset your password: "
            f"http://127.0.0.1:5013/inventory/admin/reset-password/{reset_token}")

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


@inventory_admin_api.post("/inventory/admin/reset-password")
def user_forgot_password():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            email = request.form.get("email")
            existing_user = InventoryAdminLogin.query.filter_by(email=email).first()

            if not existing_user:
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


@inventory_admin_api.route("/inventory/admin/reset-password/<token>", methods=['GET', 'POST'])
def user_link_forgot_password(token):
    try:

        email = s.loads(token, salt='password-reset', max_age=1800)

        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(email=email).first()

        if user_:
            if request.method == 'GET':
                return render_template("reset_password.html")

            user_.password = pbkdf2_sha256.hash(request.form["new_password"])
            db.session.commit()

            return '<h1>Change Password Successfully!</h1>'
        else:
            return jsonify(error={"Message": "Email not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


@inventory_admin_api.put("/inventory/admin/change-password/<int:login_id>")
def user_change_password(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Assuming you have a CustomerLogin model
            user_to_change_pass = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

            if user_to_change_pass:

                # Validate old password
                old_password = request.form.get("old_password")
                if old_password and not pbkdf2_sha256.verify(old_password, user_to_change_pass.password):
                    return jsonify(error={"message": "Incorrect old password."}), 400

                # Update the password if a new password is provided
                new_password = request.form.get("new_password")
                if new_password:
                    user_to_change_pass.password = pbkdf2_sha256.hash(new_password)

                # Commit the changes to the database
                db.session.commit()

                return jsonify(success={"message": "Successfully change the password."}), 200
            else:
                return jsonify(error={"message": "User not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update user password. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


