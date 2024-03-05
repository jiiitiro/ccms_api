from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
import random
from dotenv import load_dotenv, find_dotenv
import os
from flask_jwt_extended import JWTManager, create_access_token
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)

app.config.from_pyfile('config.cfg')

# os environment here
load_dotenv(find_dotenv())

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")

mail = Mail(app)

s = URLSafeTimedSerializer('Thisisasecret!')

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI","sqlite:///posts.db")
db = SQLAlchemy()
db.init_app(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)


# Define the Customer class
class Customer(db.Model):
    __tablename__ = 'customer_tbl'
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    middle_name = db.Column(db.String(250), nullable=True)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_confirm = db.Column(db.Boolean, default=False)

    # Define relationship to the Booking class
    bookings = db.relationship('Booking', back_populates='customer', lazy=True)


# Define the Booking class
class Booking(db.Model):
    __tablename__ = 'booking_tbl'
    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service_tbl.service_id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    booking_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(250), nullable=False)

    # Add a relationship to the Customer class
    customer = db.relationship('Customer', back_populates='bookings', lazy=True)
    services = db.relationship('Service', back_populates="bookings",  lazy=True)


# Define the Employee class
class Employee(db.Model):
    __tablename__ = 'employee_tbl'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    middle_name = db.Column(db.String(250), nullable=True)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)

    attendances = db.relationship('Attendance', back_populates='employee', lazy=True)
    schedules = db.relationship('Schedule', back_populates='employee', lazy=True)
    payrolls = db.relationship('Payroll', back_populates='employee', lazy=True)


class Attendance(db.Model):
    __tablename__ = 'attendance_tbl'
    attendance_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    work_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='attendances', lazy=True)


class Payroll(db.Model):
    __tablename__ = 'payroll_tbl'
    payroll_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    basic_pay = db.Column(db.Float, nullable=False)
    overtime_hours = db.Column(db.Float, nullable=False, default=0)
    overtime_pay = db.Column(db.Float, nullable=False, default=0)
    allowances = db.Column(db.Float, nullable=False, default=0)
    gross_pay = db.Column(db.Float, nullable=False, default=0)

    # Government Mandated Contributions
    sss_contribution = db.Column(db.Float, nullable=False, default=0)
    philhealth_contribution = db.Column(db.Float, nullable=False, default=0)
    pagibig_contribution = db.Column(db.Float, nullable=False, default=0)

    # Tax Deductions
    withholding_tax = db.Column(db.Float, nullable=False, default=0)

    # Other Deductions
    other_deductions = db.Column(db.Float, nullable=False, default=0)

    # Net Pay
    net_pay = db.Column(db.Float, nullable=False, default=0)

    # Additional Fields
    tax_refund = db.Column(db.Float, nullable=True, default=0)
    thirteenth_month_pay = db.Column(db.Float, nullable=True, default=0)

    status = db.Column(db.String(50), nullable=False)

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='payrolls', lazy=True)


# Define the Service class
class Service(db.Model):
    __tablename__ = 'service_tbl'
    service_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # in hours
    price = db.Column(db.Float, nullable=False)

    bookings = db.relationship('Booking', back_populates='services', lazy=True)


# Define the Schedule class
class Schedule(db.Model):
    __tablename__ = 'schedule_tbl'
    schedule_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    work_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='schedules', lazy=True)


# Define the Inventory class
class Inventory(db.Model):
    __tablename__ = 'inventory_tbl'
    inventory_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)


# Define the Billing class
class Billing(db.Model):
    __tablename__ = 'billing_tbl'
    invoice_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking_tbl.booking_id'))
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(100), nullable=False)


# Define the payroll_login_tbl
class PayrollAdminLogin(db.Model):
    __tablename__ = "payroll_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class BillingAdminLogin(db.Model):
    __tablename__ = "billing_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class EmployeeAdminLogin(db.Model):
    __tablename__ = "employee_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class CustomerAdminLogin(db.Model):
    __tablename__ = "customer_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class InventoryAdminLogin(db.Model):
    __tablename__ = "inventory_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


# admin_login_tbl
@app.get("/customer/admin-login")
def get_all_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        response_data = db.session.execute(db.select(CustomerAdminLogin)).scalars().all()
        user_data = [
            {
                "login_id": data.login_id,
                "email": data.email,
                "password": data.password,
                "role": data.role,
                "is_active": data.is_active,
            } for data in response_data
        ]
        response = jsonify({"Customer_Admin_Login_Data": user_data})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@app.get("/customer/admin-login/<int:login_id>")
def get_spec_cust_admin_data(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        login_data = db.session.query(CustomerAdminLogin).filter_by(login_id=login_id).first()
        if login_data:
            login_data_dict = {
                "login_id": login_data.login_id,
                "email": login_data.email,
                "password": login_data.password,
                "role": login_data.role,
                "is_active": login_data.is_active,
            }
            response = jsonify({"login_data": login_data_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Customer not found"}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@app.post("/customer/admin-login/register")
def register_customer_admin_login():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            new_login = CustomerAdminLogin(
                email=request.form.get("email"),
                password=request.form.get("password"),
                role=request.form.get("role"),
            )
            db.session.add(new_login)
            db.session.commit()

            new_login_dict = [
                {
                    "login_id": new_login.login_id,
                    "email": new_login.email,
                    "password": new_login.password,
                    "role": new_login.role,
                    "is_active": new_login.is_active,
                }]

            return jsonify(
                success={"message": "Admin/staff added successfully", "customer": new_login_dict}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to add the new admin/staff login. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@app.put("/customer/admin-login/<int:login_id>")
def update_cust_admin_login(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Assuming you have a CustomerLogin model
            login_to_update = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

            if login_to_update:
                # Update the login details based on the request data
                login_to_update.email = request.form.get("email")
                login_to_update.password = request.form.get("password")
                login_to_update.role = request.form.get("role")
                # Convert the 'is_active' string to a boolean
                is_active_str = request.form.get("is_active")
                login_to_update.is_active = True if is_active_str.lower() == 'true' else False

                # Commit the changes to the database
                db.session.commit()

                login_to_update_dict = {
                    "login_id": login_to_update.login_id,
                    "email": login_to_update.email,
                    "password": login_to_update.password,
                    "role": login_to_update.role,
                    "is_active": login_to_update.is_active,
                }

                return jsonify(success={"message": "Customer admin login updated successfully",
                                        "login_date": login_to_update_dict}), 200
            else:
                return jsonify(error={"message": "Customer admin login not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update customer admin login. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@app.delete("/customer/admin-login/<int:login_id>")
def delete_cust_admin_login_data(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        cust_admin_to_delete = db.session.execute(db.select(CustomerAdminLogin).
                                                  where(CustomerAdminLogin.login_id == login_id)).scalar()
        if cust_admin_to_delete:
            db.session.delete(cust_admin_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted the customer admin login data."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# customer
# get all customer table data
@app.get("/customer")
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
@app.get("/customer/<int:customer_id>")
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
@app.post("/customer/register")
def register_customer():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:

            # Check if the email already exists
            existing_customer = Customer.query.filter_by(email=request.form.get("email")).first()

            if existing_customer:
                return jsonify(error={"message": "Email already exists. Please use a different email address."}), 400

            email = request.form['email']
            token = s.dumps(email, salt='email-confirm')

            link = url_for('confirm_email', token=token, _external=True)

            # Construct the email message
            subject = 'Confirm Email'
            body = f'Your confirmation link is {link}'
            recipient_email = email

            # Create the MIMEText object
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, 'plain'))

            msg['From'] = MY_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Connect to the SMTP server and send the email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(MY_EMAIL, MY_PASSWORD)
                server.sendmail(MY_EMAIL, recipient_email, msg.as_string())

            new_customer = Customer(
                first_name=request.form.get("first_name"),
                middle_name=request.form.get("middle_name"),
                last_name=request.form.get("last_name"),
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
@app.get("/customer/confirm_email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)

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
@app.post("/customer/login")
def login_customer():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            customer = Customer.query.filter(Customer.email == request.form.get("email")).first()

            if customer and pbkdf2_sha256.verify(request.form.get("password"), customer.password):
                # access_token = create_access_token(identity=customer.customer_id)
                # return {"access_token": access_token}
                return jsonify(success={"message": "email and password are match."}), 200

            return jsonify(error={"message": "Invalid credentials."}), 401
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to register a new customer. Error: {str(e)}"}), 500
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


@app.put("/customer/<int:customer_id>")
def update_customer(customer_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Assuming you have a CustomerLogin model
            customer_to_update = Customer.query.filter_by(customer_id=customer_id).first()

            if customer_to_update:

                # Check if the new email is already taken by another customer
                new_email = request.form.get("email")
                existing_customer_with_email = Customer.query.filter(Customer.customer_id != customer_id,
                                                                     Customer.email == new_email).first()

                if existing_customer_with_email:
                    return jsonify(
                        error={"message": "Email already exists. Please use a different email address."}), 400

                # Validate old password
                old_password = request.form.get("old_password")
                if old_password and not pbkdf2_sha256.verify(old_password, customer_to_update.password):
                    return jsonify(error={"message": "Incorrect old password."}), 400

                # Update the login details based on the request data
                customer_to_update.first_name = request.form.get("first_name")
                customer_to_update.middle_name = request.form.get("middle_name")
                customer_to_update.last_name = request.form.get("last_name")
                old_email = customer_to_update.email
                customer_to_update.email = new_email

                # Update the password if a new password is provided
                new_password = request.form.get("new_password")
                if new_password:
                    customer_to_update.password = pbkdf2_sha256.hash(new_password)

                customer_to_update.phone = request.form.get("phone")
                # Convert the 'is_active' string to a boolean
                is_active_str = request.form.get("is_active")
                customer_to_update.is_active = True if is_active_str.lower() == 'true' else False

                # Commit the changes to the database
                db.session.commit()

                # Send email notification about the email change
                send_email_notification(old_email, new_email)

                login_to_update_dict = {
                    "customer_id": customer_to_update.customer_id,
                    "first_name": customer_to_update.first_name,
                    "middle_name": customer_to_update.middle_name,
                    "last_name": customer_to_update.last_name,
                    "email": customer_to_update.email,
                    "is_active": customer_to_update.is_active,
                    "email_confirm": customer_to_update.email_confirm,
                }

                return jsonify(success={"message": "Customer information updated successfully",
                                        "login_data": login_to_update_dict}), 200
            else:
                return jsonify(error={"message": "Customer not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update customer login. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@app.delete("/customer/<int:customer_id>")
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


# Get all payroll_login_tbl data
@app.route("/payroll_login")
def get_payroll_login_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        user_data = db.session.execute(db.select(PayrollAdminLogin)).scalars().all()
        payroll_login_dict = [
            {
                'login_id': data.login_id,
                'email': data.email,
                'password': data.password,
                'role': data.role,
                'is_active': data.is_active,
            } for data in user_data]
        response = jsonify({'user_data': payroll_login_dict})
        return response
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# Get all payroll table data
@app.route('/payroll')
def payroll_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        payroll_data = db.session.execute(db.select(Payroll)).scalars().all()
        payroll_data_dict = [{
            'payroll_id': data.payroll_id,
            'employee_id': data.employee_id,
            'period_start': data.period_start,
            'period_end': data.period_end,
            'basic_pay': data.basic_pay,
            'overtime_hours': data.overtime_hours,
            'overtime_pay': data.overtime_pay,
            'allowances': data.allowances,
            'gross_pay': data.gross_pay,
            'sss_contribution': data.sss_contribution,
            'philhealth_contribution': data.philhealth_contribution,
            'pagibig_contribution': data.pagibig_contribution,
            'witholding_tax': data.witholding_tax,
            'other_deduction': data.other_deduction,
            'net_pay': data.net_pay,
            'thirteenth_month_pay': data.thirteenth_month_pay,
            'status': data.status
        } for data in payroll_data]
        response = jsonify(payroll_data_dict)
        return response
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == "__main__":
    app.run(debug=True, port=5013)



