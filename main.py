from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import random
from dotenv import load_dotenv, find_dotenv
import os

app = Flask(__name__)

# os environment here
load_dotenv(find_dotenv())

# api-key
API_KEY = os.environ.get('API_KEY')


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI","sqlite:///posts.db")
db = SQLAlchemy()
db.init_app(app)


# Define the Customer class
class Customer(db.Model):
    __tablename__ = 'customer_tbl'
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), nullable=False)
    bookings = db.relationship('Booking', backref='customer', lazy=True)


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


# Define the Employee class
class Employee(db.Model):
    __tablename__ = 'employee_tbl'
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    schedules = db.relationship('Schedule', backref='employee', lazy=True)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True)


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
    employee = db.relationship('Employee', backref=db.backref('payrolls', lazy=True))


class Login(db.Model):
    __tablename__ = 'login_tbl'
    login_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Define relationship to the Customer, nullable since not all logins will be linked to a customer
    customer = db.relationship('Customer', backref='login', uselist=False)

    # Define relationship to the Employee, nullable since not all logins will be linked to an employee
    employee = db.relationship('Employee', backref='login', uselist=False)


# Define the Service class
class Service(db.Model):
    __tablename__ = 'service_tbl'
    service_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # in hours
    price = db.Column(db.Float, nullable=False)
    bookings = db.relationship('Booking', backref='service', lazy=True)


# Define the Schedule class
class Schedule(db.Model):
    __tablename__ = 'schedule_tbl'
    schedule_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    work_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)


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
class PayrollLogin(db.Model):
    __tablename__ = "payroll_login_tbl"
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


# Get all payroll_login_tbl data
@app.route("/payroll_login")
def get_payroll_login_data():
    api_key_params = request.args.get("api-key")
    if api_key_params == API_KEY:
        user_data = db.session.execute(db.select(PayrollLogin)).scalars().all()
        payroll_login_dict = [
            {
                'login_id': data.login_id,
                'email': data.email,
                'password': data.password,
                'role': data.role,
                'is_active': data.is_active
            } for data in user_data]
        response = jsonify({'user_data': payroll_login_dict})
        return response
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# Get all payroll table data
@app.route('/payroll')
def payroll_data():
    api_key_params = request.args.get("api-key")
    if api_key_params == API_KEY:
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
    app.run(debug=False, port=5013)




