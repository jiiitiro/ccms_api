import os
from email.mime.multipart import MIMEMultipart
from db import db
from flask import Blueprint, jsonify, render_template, redirect, url_for
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import flash, request, session
from models import CustomerAdminLogin, BillingAdminLogin, EmployeeAdminLogin, InventoryAdminLogin, PayrollAdminLogin
from models.admin_logins_models import SuperadminLogin
from models.activity_logs_models import SuperadminActivityLogs, BillingAdminActivityLogs, PayrollAdminActivityLogs, \
    CustomerAdminActivityLogs, EmployeeAdminActivityLogs
from forms import SuperadminLoginForm, ForgotPasswordForm, ChangePasswordForm, RegistrationForm
import smtplib
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
import plotly.graph_objs as go
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from functions import log_activity

superadmin_api = Blueprint('superadmin_api', __name__)
login_manager = LoginManager()

# superadmin api-key
API_KEY = os.environ.get('SUPERADMIN_API_KEY')
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")
SUPERADMIN_EMAIL = os.environ.get("SUPERADMIN_EMAIL")
SUPERADMIN_PASSWORD = os.environ.get("SUPERADMIN_PASSWORD")

s = URLSafeTimedSerializer('Thisisasecret!')


def custom_unauthorized_handler(e):
    return render_template('401.html'), 401  # Render custom HTML for unauthorized access, return HTTP status code 401


def login_required_with_custom_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return render_template('401.html'), 401
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(login_id):
    return db.get_or_404(SuperadminLogin, login_id)


@superadmin_api.get("/superadmin/dashboard")
@login_required_with_custom_error
def dashboard_superadmin():
    # Query the database to get the necessary data for the bar chart
    active_customers = db.session.query(CustomerAdminLogin).filter_by(is_active=True).count()
    inactive_customers = db.session.query(CustomerAdminLogin).filter_by(is_active=False).count()

    active_billing_admins = db.session.query(BillingAdminLogin).filter_by(is_active=True).count()
    inactive_billing_admins = db.session.query(BillingAdminLogin).filter_by(is_active=False).count()

    active_inventory_admins = db.session.query(InventoryAdminLogin).filter_by(is_active=True).count()
    inactive_inventory_admins = db.session.query(InventoryAdminLogin).filter_by(is_active=False).count()

    active_employees = db.session.query(EmployeeAdminLogin).filter_by(is_active=True).count()
    inactive_employees = db.session.query(EmployeeAdminLogin).filter_by(is_active=False).count()

    active_payroll = db.session.query(PayrollAdminLogin).filter_by(is_active=True).count()
    inactive_payroll = db.session.query(PayrollAdminLogin).filter_by(is_active=False).count()

    # Create the bar chart data
    data_num_user = [
        go.Bar(
            x=['Customers', 'Billing', 'Inventory', 'Employees', 'Payroll'],
            y=[active_customers, active_billing_admins, active_inventory_admins, active_employees, active_payroll],
            name='Active'
        ),
        go.Bar(
            x=['Customers', 'Billing', 'Inventory', 'Employees', 'Payroll'],
            y=[inactive_customers, inactive_billing_admins, inactive_inventory_admins, inactive_employees, inactive_payroll],
            name='Inactive'
        )
    ]

    # Calculate maximum counts for active and inactive users
    max_active_count = max(active_customers, active_billing_admins, active_inventory_admins, active_employees,
                           active_payroll)
    max_inactive_count = max(inactive_customers, inactive_billing_admins, inactive_inventory_admins, inactive_employees,
                             inactive_payroll)

    # Determine the maximum overall count
    max_count = max(max_active_count, max_inactive_count)

    # Calculate a suitable increment for the ticks
    tick_increment = max_count // 10 + 1

    # Create layout with dynamic tick values
    layout_num_user = go.Layout(
        barmode='group',
        xaxis=dict(title='Subsystem'),
        yaxis=dict(
            title='Number of Users',
            tickmode='linear',  # Use linear mode for automatic tick calculation
            dtick=tick_increment,  # Set tick increment dynamically
        ),
        showlegend=True,
        autosize=True,  # Automatically adjust the size
        margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins for better fit
    )

    chart_num_user = go.Figure(data=data_num_user, layout=layout_num_user)

    # Convert the Plotly chart to JSON
    chart_num_user_json = chart_num_user.to_json()

    # Query the database to get the necessary data for the bar chart
    user_types = ['Customer', 'Billing', 'Inventory', 'Employee', 'Payroll']
    roles = ['Admin', 'Staff']

    admin_counts = {role: [] for role in roles}

    for user_type in user_types:
        for role in roles:
            admin_count = db.session.query(globals()[f"{user_type}AdminLogin"]).filter_by(role=role).count()
            admin_counts[role].append(admin_count)

    # Create the bar chart data
    data_roles = [
        go.Bar(
            x=user_types,
            y=admin_counts['Admin'],
            name='Admin',
            marker=dict(color='#2ca02c')  # Blue color for Admin
        ),
        go.Bar(
            x=user_types,
            y=admin_counts['Staff'],
            name='Staff',
            marker=dict(color='#9467bd')  # Blue color for Admin
        )
    ]

    layout_roles = go.Layout(
        barmode='stack',
        xaxis=dict(title='Subsystem'),
        yaxis=dict(title='Number of Users'),
        showlegend=True,
        autosize=True,  # Automatically adjust the size
        margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins for better fit
    )

    chart1 = go.Figure(data=data_roles, layout=layout_roles)

    # Convert the Plotly chart to JSON
    chart_roles_json = chart1.to_json()

    return render_template("superadmin_dashboard.html", chart_num_user_json=chart_num_user_json, chart_roles_json=chart_roles_json)


@superadmin_api.get("/superadmin/billing")
@login_required
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


@superadmin_api.get("/superadmin/customer")
@login_required
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
@login_required
def activate_customer_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Activate admin account for customer subsystem with an id of {admin_user.login_id}")

    return redirect(url_for("superadmin_api.customer_superadmin"))


@superadmin_api.post("/superadmin/customer/deactivate/<int:login_id>")
@login_required
def deactivate_customer_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = False
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Deactivate admin account for customer subsystem with an id of {admin_user.login_id}")

    return redirect(url_for("superadmin_api.customer_superadmin"))


@superadmin_api.get("/superadmin/employee")
@login_required
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


@superadmin_api.get("/superadmin/inventory")
@login_required
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


@superadmin_api.get("/superadmin/payroll")
@login_required
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


@superadmin_api.post("/superadmin/billing-admin/activate/<int:login_id>")
@login_required
def activate_billing_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = BillingAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = True
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Activate admin account for billing subsystem with an id of {user_.login_id}")

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/billing-admin/deactivate/<int:login_id>")
@login_required
def deactivate_billing_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = BillingAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = False
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Deactivate admin account for billing subsystem with an id of {user_.login_id}")

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/employee-admin/activate/<int:login_id>")
@login_required
def activate_employee_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = EmployeeAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = True
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Activate admin account for employee subsystem with an id of {user_.login_id}")

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/inventory-admin/activate/<int:login_id>")
@login_required
def activate_inventory_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = True
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Activate admin account for inventory subsystem with an id of {user_.login_id}")

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/inventory-admin/deactivate/<int:login_id>")
@login_required
def deactivate_inventory_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = False
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Deactivate admin account for inventory subsystem with an id of {user_.login_id}")

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/payroll-admin/activate/<int:login_id>")
@login_required
def activate_payroll_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = PayrollAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = True
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Activate admin account for payroll subsystem with an id of {user_.login_id}")

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/payroll-admin/deactivate/<int:login_id>")
@login_required
def deactivate_payroll_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = PayrollAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            login_id = session.get("login_id")
            if login_id is None:
                return jsonify(success=False, message="Login id not found."), 404

            user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            user_.is_active = False
            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Deactivate admin account for payroll subsystem with an id of {user_.login_id}")

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

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            # Query the database to find the user by email
            user = SuperadminLogin.query.filter_by(email=email).first()

            if not user:
                return jsonify(success=False, message="That email does not exist, please try again.")

            if user.failed_timer is not None:
                if user.failed_timer > datetime.now():
                    time_remaining = user.failed_timer - datetime.now()

                    log_activity(SuperadminActivityLogs, login_id=user.login_id,
                                 logs_description=f"Too many failed attempts {user.consecutive_failed_login}x. ")

                    return jsonify(success=False,
                                   message=f"Please try again in {time_remaining.seconds} seconds.")

            if not pbkdf2_sha256.verify(password, user.password):
                if user.consecutive_failed_login is None:
                    user.consecutive_failed_login = 0

                user.consecutive_failed_login += 1

                if user.consecutive_failed_login >= 3:
                    user.failed_timer = datetime.now() + timedelta(seconds=30)

                    log_activity(SuperadminActivityLogs, login_id=user.login_id,
                                 logs_description=f"Password incorrect {user.consecutive_failed_login}x times.")

                    return jsonify(success=False, message=f"Password incorrect {user.consecutive_failed_login}x, "
                                                          f"please try again in 30secs.")

                log_activity(SuperadminActivityLogs, login_id=user.login_id,
                             logs_description=f"Password incorrect {user.consecutive_failed_login} times.")

                return jsonify(success=False,
                               message=f"Password incorrect {user.consecutive_failed_login}x, please try again.")

            # Reset consecutive_failed_login and failed_timer
            user.consecutive_failed_login = 0
            user.failed_timer = None

            db.session.commit()
            # Login the user
            login_user(user)

            # Store user login_id in session storage
            session['login_id'] = user.login_id
            print(session['login_id'])

            # Return a JSON response indicating successful login
            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"User logged in.")

            return jsonify(success=True)

        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=f"An error occurred: {str(e)}")

    return render_template("superadmin_login_1.html", form=form)


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
            log_activity(SuperadminActivityLogs, login_id=user.login_id,
                         logs_description=f"Forgot password")

            reset_token = s.dumps(email, salt='password-reset')

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
                                <h1>Hello {user.name},</h1>
                                <p>Click the following link to reset your password: <a href="{BASE_URL}/superadmin/reset-password/{reset_token}">Reset Password</a></p>
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
    # Retrieve user login id from session storage
    user_login_id = session.get('login_id')

    if user_login_id is None:
        return jsonify(success=False, message="User not logged in.")

    # Log the logout activity
    log_activity(SuperadminActivityLogs, login_id=user_login_id,
                 logs_description="User logged out.")

    # Clear user information from session storage
    session.pop('login_id', None)

    logout_user()

    return redirect(url_for("superadmin_api.superadmin_login"))


@superadmin_api.get("/superadmin/payroll-admin/account-activation/<token>")
def account_activation(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=7200)

        # Find the user with the confirmed email
        user = PayrollAdminLogin.query.filter_by(email=email).first()

        if user:
            # Update the email_confirm status to True
            user.is_active = True
            db.session.commit()

            return '<h1>Account Activated Successfully!</h1>'
        else:
            return jsonify(error={"Message": "user not found."}), 404

    except SignatureExpired:
        return '<h1>Token is expired.</h1>'


# Function to generate a random password
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


@superadmin_api.route("/superadmin/user-registration", methods=['GET', 'POST'])
@login_required
def user_registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            name = form.name.data
            email = form.email.data
            role = form.role.data
            subsystem = form.subsystem.data

            # Query the database to find the user by email and subsystem
            if subsystem == 'billing':
                user = BillingAdminLogin.query.filter_by(email=email).first()
            elif subsystem == 'customer':
                user = CustomerAdminLogin.query.filter_by(email=email).first()
            elif subsystem == 'employee':
                user = EmployeeAdminLogin.query.filter_by(email=email).first()
            elif subsystem == 'inventory':
                user = InventoryAdminLogin.query.filter_by(email=email).first()
            elif subsystem == 'payroll':
                user = PayrollAdminLogin.query.filter_by(email=email).first()
            else:
                # Handle if subsystem value is invalid
                return jsonify(success=False, message="Invalid subsystem value.")

            if user:
                return jsonify(success=False, message="Email already exists. Please use a different email address.")

            # Generate a random password
            random_password = generate_random_password()

            # Create new user based on the subsystem
            new_login = None
            if subsystem == 'billing':
                new_login = BillingAdminLogin(
                    name=name,
                    email=email,
                    password=pbkdf2_sha256.hash(random_password),
                    role=role,
                    is_active=True,
                )
            elif subsystem == 'customer':
                new_login = CustomerAdminLogin(
                    name=name,
                    email=email,
                    password=pbkdf2_sha256.hash(random_password),
                    role=role,
                    is_active=True,
                )
            elif subsystem == 'employee':
                new_login = EmployeeAdminLogin(
                    name=name,
                    email=email,
                    password=pbkdf2_sha256.hash(random_password),
                    role=role,
                    is_active=True,
                )
            elif subsystem == 'inventory':
                new_login = InventoryAdminLogin(
                    name=name,
                    email=email,
                    password=pbkdf2_sha256.hash(random_password),
                    role=role,
                    is_active=True,
                )
            elif subsystem == 'payroll':
                new_login = PayrollAdminLogin(
                    name=name,
                    email=email,
                    password=pbkdf2_sha256.hash(random_password),
                    role=role,
                    is_active=True,
                )

            # Add the new user to the database
            db.session.add(new_login)

            login_id = session.get("login_id")
            print(login_id)
            if login_id is None:
                return jsonify(success=False, message="New to provide login id."), 404

            superadmin_user = SuperadminLogin.query.filter_by(login_id=login_id).first()

            if not superadmin_user:
                return jsonify(success=False, message="Superadmin user not found."), 404

            db.session.commit()

            log_activity(SuperadminActivityLogs, login_id=login_id,
                         logs_description=f"Add user for {subsystem} subsystem with an id of {new_login.login_id}")

            recipient_email = form.email.data

            # Create a confirmation token including subsystem information
            token_data = {'email': email, 'subsystem': subsystem}
            token = s.dumps(token_data, salt='email-confirm')

            subject = 'Confirm Email'
            # Construct the HTML body with appropriate formatting
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
                    <h1>Hello {new_login.name},</h1>
                    <p>Click the following link to confirm your email: <a href="{BASE_URL}/superadmin/user-registration/confirm-email/{token}">Confirm Email</a></p>
                    <p>This is your randomly generated password:</p>
                    <p class="password">{random_password}</p>
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
                # Rollback the session in case of an error sending email
                db.session.rollback()
                print(f"Failed to send email notification. Error: {str(e)}")

            # Return success message with generated password
            return jsonify(success=True, message="User registered successfully. "
                                                 "Please inform the user to check their email for confirmation.")

        except Exception as e:
            # Rollback the session in case of an error during registration
            db.session.rollback()
            print({str(e)})
            return jsonify(error={"Message": f"Failed to register user. Error: {str(e)}"}), 500

    return render_template("registration.html", form=form)


@superadmin_api.get("/superadmin/user-registration/confirm-email/<token>")
def confirm_email(token):
    try:
        # Deserialize the token to retrieve email and subsystem
        token_data = s.loads(token, salt='email-confirm', max_age=1800)

        email = token_data['email']
        subsystem = token_data['subsystem']

        # Find the user with the confirmed email based on the subsystem
        user = None
        if subsystem == 'billing':
            user = BillingAdminLogin.query.filter_by(email=email).first()
        elif subsystem == 'customer':
            user = CustomerAdminLogin.query.filter_by(email=email).first()
        elif subsystem == 'employee':
            user = EmployeeAdminLogin.query.filter_by(email=email).first()
        elif subsystem == 'inventory':
            user = InventoryAdminLogin.query.filter_by(email=email).first()
        elif subsystem == 'payroll':
            user = PayrollAdminLogin.query.filter_by(email=email).first()

        if user:
            # Update the email_confirm status to True
            user.email_confirm = True
            db.session.commit()

            return ('<h1 style="font-family: Arial, sans-serif; font-size: 24px; color: #333; text-align: center; '
                    'margin-top: 50px;">Email Confirm Successfully!</h1>')

        else:
            return jsonify(error={"Message": "User not found."}), 404

    except SignatureExpired:
        return ('<h1 style="font-family: Arial, sans-serif; font-size: 24px; color: #333; text-align: center; '
                'margin-top: 50px;">Token Expired!</h1>')


@superadmin_api.post("/superadmin/payroll/activate/<int:login_id>")
@login_required
def activate_payroll_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Activate admin account for payroll subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully activated the payroll admin account.")
    else:
        return jsonify(success=False, message="Payroll admin account not found."), 404


@superadmin_api.post("/superadmin/payroll/deactivate/<int:login_id>")
@login_required
def deactivate_payroll_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = False
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Deactivate admin account for customer subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully deactivated the payroll admin account.")
    else:
        return jsonify(success=False, message="Payroll admin account not found."), 404


@superadmin_api.post("/superadmin/payroll/delete/<int:login_id>")
@login_required
def delete_payroll_admin_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        db.session.delete(admin_user)
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Delete admin account for payroll subsystem with an id of {admin_user.login_id}")


        return jsonify(success=True, message="Successfully deleted the payroll admin account.")
    else:
        return jsonify(success=False, message="Payroll admin account not found."), 404


@superadmin_api.post("/superadmin/customer-admin/activate/<int:login_id>")
@login_required
def activate_customer_admin(login_id):
    # Find the customer with the confirmed email
    user_ = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

    if user_:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        user_.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Activate admin account for customer subsystem with an id of {user_.login_id}")

        return jsonify(success=True, message="Successfully activated the customer admin account.")
    else:
        return jsonify(success=False, message="Customer admin account not found."), 404


@superadmin_api.post("/superadmin/customer-admin/deactivate/<int:login_id>")
@login_required
def deactivate_customer_admin(login_id):
    # Find the customer with the confirmed email
    user_ = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

    if user_:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        # Update the email_confirm status to True
        user_.is_active = False
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Deactivate admin account for customer subsystem with an id of {user_.login_id}")

        return jsonify(success=True, message="Successfully deactivated the customer admin account.")
    else:
        return jsonify(success=False, message="Customer admin account not found."), 404


@superadmin_api.post("/superadmin/customer-admin/delete/<int:login_id>")
@login_required
def delete_customer_admin_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        db.session.delete(admin_user)
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Delete admin account for customer subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully deleted the customer admin account.")
    else:
        return jsonify(success=False, message="Customer admin account not found."), 404


@superadmin_api.post("/superadmin/employee/activate/<int:login_id>")
@login_required
def activate_employee_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Activate admin account for employee subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully activated the employee admin account.")
    else:
        return jsonify(success=False, message="Employee admin account not found."), 404


@superadmin_api.post("/superadmin/employee/deactivate/<int:login_id>")
@login_required
def deactivate_employee_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = False
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Deactivate admin account for employee subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully deactivated the customer admin account.")
    else:
        return jsonify(success=False, message="Employee admin account not found."), 404


@superadmin_api.post("/superadmin/employee/delete/<int:login_id>")
@login_required
def delete_employee_admin_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        db.session.delete(admin_user)
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Delete admin account for employee subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully deleted the employee admin account.")
    else:
        return jsonify(success=False, message="Employee admin account not found."), 404


@superadmin_api.post("/superadmin/inventory/activate/<int:login_id>")
@login_required
def activate_inventory_account(login_id):
    admin_user = InventoryAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Activate admin account for inventory subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully activated the inventory admin account.")
    else:
        return jsonify(success=False, message="Inventory admin account not found."), 404


@superadmin_api.post("/superadmin/inventory/deactivate/<int:login_id>")
@login_required
def deactivate_inventory_account(login_id):
    admin_user = InventoryAdminLogin.query.get(login_id)

    if admin_user:
        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Deactivate admin account for inventory subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully deactivated the inventory admin account.")
    else:
        return jsonify(success=False, message="Inventory admin account not found."), 404


@superadmin_api.post("/superadmin/inventory/delete/<int:login_id>")
@login_required
def delete_inventory_admin_account(login_id):
    admin_user = InventoryAdminLogin    .query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        db.session.delete(admin_user)
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Delete admin account for inventory subsystem with an id of {admin_user.login_id}")


        return jsonify(success=True, message="Successfully deleted the inventory admin account.")
    else:
        return jsonify(success=False, message="Inventory admin account not found."), 404


@superadmin_api.post("/superadmin/billing/activate/<int:login_id>")
@login_required
def activate_billing_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        admin_user.is_active = True
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Activate admin account for billing subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully activated the billing admin account."), 200
    else:
        return jsonify(success=False, message="Billing admin account not found."), 404


@superadmin_api.post("/superadmin/billing/deactivate/<int:login_id>")
@login_required
def deactivate_billing_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

        # Retrieve user login id from session storage
        user_login_id = session.get('login_id')

        if user_login_id is None:
            return jsonify(success=False, message="User not logged in.")

        # Log the logout activity
        log_activity(SuperadminActivityLogs, login_id=user_login_id,
                     logs_description=f"Successfully deactivated the billing admin account. User is {admin_user.name}")

        return jsonify(success=True, message="Successfully deactivated the billing admin account."), 200
    else:
        return jsonify(success=False, message="Billing admin account not found."), 404


@superadmin_api.post("/superadmin/billing/delete/<int:login_id>")
@login_required
def delete_billing_admin_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:

        login_id = session.get("login_id")
        if login_id is None:
            return jsonify(success=False, message="Login id not found."), 404

        user = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if not user:
            return jsonify(success=False, message="Superadmin user not found."), 404

        db.session.delete(admin_user)
        db.session.commit()

        log_activity(SuperadminActivityLogs, login_id=user.login_id,
                     logs_description=f"Delete admin account for billing  subsystem with an id of {admin_user.login_id}")

        return jsonify(success=True, message="Successfully deleted the billing admin account.")
    else:
        return jsonify(success=False, message="billing admin account not found."), 404


@superadmin_api.get("/superadmin/billing/activity-logs")
@login_required
def billing_activity_logs():
    activity_logs = BillingAdminActivityLogs.query.all()

    billing_logs_data = [{
        "log_id": log.log_id,
        "admin_name": log.billing_admin.name,
        "logs_description": log.logs_description,
        "log_date": log.log_date
    } for log in activity_logs]

    return render_template("billing_activity_logs.html", result=billing_logs_data)


@superadmin_api.get("/superadmin/payroll/activity-logs")
@login_required
def payroll_activity_logs():
    activity_logs = PayrollAdminActivityLogs.query.all()

    payroll_logs_data = [{
        "log_id": log.log_id,
        "admin_name": log.payroll_admin.name,
        "logs_description": log.logs_description,
        "log_date": log.log_date
    } for log in activity_logs]

    return render_template("payroll_activity_logs.html", result=payroll_logs_data)


@superadmin_api.get("/superadmin/customer/activity-logs")
@login_required
def customer_activity_logs():
    activity_logs = CustomerAdminActivityLogs.query.all()

    customer_logs_data = [{
        "log_id": log.log_id,
        "admin_name": log.customer_admin.name,
        "logs_description": log.logs_description,
        "log_date": log.log_date
    } for log in activity_logs]

    return render_template("customer_activity_logs.html", result=customer_logs_data)


@superadmin_api.get("/superadmin/employee/activity-logs")
@login_required
def employee_activity_logs():
    activity_logs = EmployeeAdminActivityLogs.query.all()

    employee_logs_data = [{
        "log_id": log.log_id,
        "admin_name": log.employee_admin.name,
        "logs_description": log.logs_description,
        "log_date": log.log_date
    } for log in activity_logs]

    return render_template("employee_activity_logs.html", result=employee_logs_data)


@superadmin_api.get("/superadmin/inventory/activity-logs")
@login_required
def inventory_activity_logs():
    activity_logs = EmployeeAdminActivityLogs.query.all()

    inventory_logs_data = [{
        "log_id": log.log_id,
        "admin_name": log.inventory_admin.name,
        "logs_description": log.logs_description,
        "log_date": log.log_date
    } for log in activity_logs]

    return render_template("inventory_activity_logs.html", result=inventory_logs_data)


@superadmin_api.get("/superadmin/activity-logs")
@login_required
def superadmin_activity_logs():
    activity_logs = SuperadminActivityLogs.query.all()

    superadmin_logs_data = [{
        "log_id": log.log_id,
        "admin_name": log.superadmin.name,
        "logs_description": log.logs_description,
        "log_date": log.log_date
    } for log in activity_logs]

    return render_template("superadmin_activity_logs.html", result=superadmin_logs_data)


@superadmin_api.post("/superadmin/change-password")
@login_required
def superadmin_change_password():
    try:
        login_id = session.get("login_id")

        query_data = SuperadminLogin.query.filter_by(login_id=login_id).first()

        if query_data is None:
            return jsonify(success=False, message="Login id not found."), 404

        old_password = request.form.get("old_password")
        if old_password and not pbkdf2_sha256.verify(old_password, query_data.password):
            return jsonify(success=False, message="Incorrect old password."), 400

        new_password = request.form.get("new_password")
        if new_password:
            query_data.password = pbkdf2_sha256.hash(new_password)

        db.session.commit()

        return jsonify(success=True, message="Successfully update your password")

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500









