import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import flash, Flask, request
from models import db, CustomerAdminLogin, BillingAdminLogin, EmployeeAdminLogin, InventoryAdminLogin, PayrollAdminLogin
from models.ccsms_models import SuperadminLogin
from forms import SuperadminLoginForm, ForgotPasswordForm, ChangePasswordForm
import smtplib
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired



superadmin_api = Blueprint('superadmin_api', __name__)

# superadmin api-key
API_KEY = os.environ.get('SUPERADMIN_API_KEY')
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")

s = URLSafeTimedSerializer('Thisisasecret!')

# @superadmin_api.get("/superadmin/login")
# def login_superadmin():
#     return render_template("superadmin_login.html")


@superadmin_api.get("/superadmin/dashboard")
def dashboard_superadmin():
    return render_template("superadmin_dashboard.html")


@superadmin_api.get("/superadmin/billing")
def billing_superadmin():
    billing_admin_logins = BillingAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in billing_admin_logins
    ]

    return render_template("billing_tables.html", result=result)


@superadmin_api.post("/superadmin/billing/activate/<int:login_id>")
def activate_billing_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.billing_superadmin"))


@superadmin_api.post("/superadmin/billing/deactivate/<int:login_id>")
def deactivate_billing_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.billing_superadmin"))


@superadmin_api.get("/superadmin/customer")
def customer_superadmin():
    customer_admin_logins = CustomerAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in customer_admin_logins
    ]
    return render_template("customer_tables.html", result=result)


@superadmin_api.post("/superadmin/customer/activate/<int:login_id>")
def activate_customer_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.customer_superadmin"))


@superadmin_api.post("/superadmin/customer/deactivate/<int:login_id>")
def deactivate_customer_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.customer_superadmin"))


@superadmin_api.get("/superadmin/employee")
def employee_superadmin():
    employee_admin_logins = EmployeeAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in employee_admin_logins
    ]
    return render_template("employee_tables.html", result=result)


@superadmin_api.post("/superadmin/employee/activate/<int:login_id>")
def activate_employee_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.employee_superadmin"))


@superadmin_api.post("/superadmin/employee/deactivate/<int:login_id>")
def deactivate_employee_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.employee_superadmin"))


@superadmin_api.get("/superadmin/inventory")
def inventory_superadmin():
    inventory_admin_logins = InventoryAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in inventory_admin_logins
    ]
    return render_template("inventory_tables.html", result=result)


@superadmin_api.post("/superadmin/inventory/activate/<int:login_id>")
def activate_inventory_account(login_id):
    admin_user = InventoryAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.inventory_superadmin"))


@superadmin_api.post("/superadmin/inventory/deactivate/<int:login_id>")
def deactivate_inventory_account(login_id):
    admin_user = InventoryAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.inventory_superadmin"))


@superadmin_api.get("/superadmin/payroll")
def payroll_superadmin():
    payroll_admin_logins = PayrollAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in payroll_admin_logins
    ]

    return render_template("payroll_tables.html", result=result)


@superadmin_api.post("/superadmin/payroll/activate/<int:login_id>")
def activate_payroll_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.payroll_superadmin"))


@superadmin_api.post("/superadmin/payroll/deactivate/<int:login_id>")
def deactivate_payroll_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.payroll_superadmin"))


@superadmin_api.post("/superadmin/customer-admin/activate/<int:login_id>")
def activate_customer_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/customer-admin/deactivate/<int:login_id>")
def deactivate_customer_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/billing-admin/activate/<int:login_id>")
def activate_billing_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = BillingAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/billing-admin/deactivate/<int:login_id>")
def deactivate_billing_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = BillingAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/employee-admin/activate/<int:login_id>")
def activate_employee_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = EmployeeAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/inventory-admin/activate/<int:login_id>")
def activate_inventory_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/inventory-admin/deactivate/<int:login_id>")
def deactivate_inventory_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/payroll-admin/activate/<int:login_id>")
def activate_payroll_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = PayrollAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/payroll-admin/deactivate/<int:login_id>")
def deactivate_payroll_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = PayrollAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.get("/superadmin/get-details")
def superadmin_get():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        superadmin_user = db.session.execute(db.select(SuperadminLogin)).scalars().all()

        superadmin_data = [
            {
                "login_id": data.login_id,
                "name": data.name,
                "email": data.email,
                "role": data.role,
                "is_active": data.is_active,
                "email_confirm": data.email_confirm,
            } for data in superadmin_user
        ]
        response = jsonify({"Superadmin_Login_Data": superadmin_data})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/register")
def register_superadmin():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            new_login = SuperadminLogin(
                name=request.form.get("name"),
                email=request.form.get("email"),
                password=pbkdf2_sha256.hash(request.form.get("password")),
                role="Superadmin",
                is_active=True,
                email_confirm=True
            )

            db.session.add(new_login)
            db.session.commit()

            new_superadmin_dict = [
                {
                    "login_id": new_login.login_id,
                    "name": new_login.name,
                    "email": new_login.email,
                    "role": new_login.role,
                    "is_active": new_login.is_active,
                    "email_confirm": new_login.email_confirm,
                }]
            return jsonify(
                success={"message": f"Superadmin successfully registered.", "superadmin_data": new_superadmin_dict}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to register. Error: {str(e)}"}), 500

    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.route("/superadmin/login", methods=["GET", "POST"])
def superadmin_login():
    form = SuperadminLoginForm()

    if request.args.get("refresh") == "true":
        flash("You have been logged out.", "info")
        return render_template("superadmin_login.html", form=form)

    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(SuperadminLogin).where(SuperadminLogin.email == form.email.data))
        user = result.scalar()

        if not user:
            return jsonify(success=False, message="That email does not exist, please try again.")
        elif not pbkdf2_sha256.verify(password, user.password):
            return jsonify(success=False, message="Password incorrect, please try again.")
        else:
            # Return a JSON response indicating successful login
            return jsonify(success=True)

    return render_template("superadmin_login.html", form=form)


@superadmin_api.route("/superadmin/forgot-password", methods=["GET", "POST"])
def superadmin_forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(SuperadminLogin).where(SuperadminLogin.email == email))
        user = result.scalar()

        if not user:
            return jsonify(success=False, message="That email does not exist, please try again.")
        else:

            reset_token = s.dumps(email, salt='password-reset')

            subject = 'Password Reset'
            body = (f"Click the following link to reset your password: "
                    f"{BASE_URL}/superadmin/reset-password/{reset_token}")

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

            return jsonify(success=True, message="Forgot password link has been sent, please check your email."
                                                 "\nREDIRECTING to login page..")

    return render_template("superadmin_forgot_password.html", form=form)


@superadmin_api.route("/superadmin/reset-password/<token>", methods=['GET', 'POST'])
def superadmin_link_forgot_password(token):
    form = ChangePasswordForm()
    try:
        email = s.loads(token, salt='password-reset', max_age=1800)

        user = SuperadminLogin.query.filter_by(email=email).first()

        if user:
            if form.validate_on_submit():
                user.password = pbkdf2_sha256.hash(form.new_password.data)
                db.session.commit()

                return '<h1>Change Password Successfully!</h1>'
            else:
                return render_template("reset_password.html", form=form)
        else:
            return jsonify(error={"Message": "Email not found."})

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


@superadmin_api.get("/superadmin/logout")
def superadmin_logout():
    return redirect(url_for("superadmin_api.superadmin_login"))


