from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import time
from sqlalchemy import Time, UniqueConstraint

db = SQLAlchemy()


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

    # Define relationship to the CustomerAddress class
    address = db.relationship('CustomerAddress', back_populates='customer', uselist=False)

    # Define relationship to the Booking class
    bookings = db.relationship('Booking', back_populates='customer', lazy=True)


class CustomerAddress(db.Model):
    __tablename__ = 'customer_address'
    address_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), unique=True, nullable=False)
    houseno_street = db.Column(db.String(100), nullable=False)
    barangay = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)

    # Define relationship to the Customer class
    customer = db.relationship('Customer', back_populates='address', uselist=False)


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
    address = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=True)
    daily_rate = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)
    de_minimis = db.Column(db.Float, nullable=True, default=0.0)

    # Relationship to other tables
    attendances = db.relationship('Attendance', back_populates='employee', lazy=True)
    schedules = db.relationship('Schedule', back_populates='employee', lazy=True)
    payrolls = db.relationship('Payroll', back_populates='employee', lazy=True)


# Define the Schedule class
class Schedule(db.Model):
    __tablename__ = 'schedule_tbl'
    schedule_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    start_time = db.Column(Time, nullable=True, default=time(8, 0, 0))  # Default start time is 08:00:00
    end_time = db.Column(Time, nullable=True, default=time(17, 0, 0))  # Default end time is 17:00:00
    day_off = db.Column(db.String(20), nullable=True, default="Friday")  # Assuming day_off can be a string (e.g., "Monday")

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='schedules', lazy=True)


class Attendance(db.Model):
    __tablename__ = 'attendance_tbl'
    attendance_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    work_date = db.Column(db.Date, nullable=False)
    login_time = db.Column(db.DateTime, nullable=True)
    logout_time = db.Column(db.DateTime, nullable=True)
    login_status = db.Column(db.String(50), nullable=True)
    logout_status = db.Column(db.String(50), nullable=True)
    tardiness = db.Column(db.Integer, nullable=True)  # Assuming tardiness is measured in minutes
    ot_hrs = db.Column(db.Float, nullable=True)

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='attendances', lazy=True)

    # Unique constraint on employee_id and work_date
    __table_args__ = (
        UniqueConstraint('employee_id', 'work_date', name='_employee_work_date_uc'),
    )


class Payroll(db.Model):
    __tablename__ = 'payroll_tbl'
    payroll_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'))
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_ot_hrs = db.Column(db.Float, nullable=False, default=0)
    base_salary = db.Column(db.Float, nullable=False, default=0)
    gross_pay = db.Column(db.Float, nullable=False, default=0)
    net_pay = db.Column(db.Float, nullable=False, default=0)
    thirteenth_month_pay = db.Column(db.Float, nullable=True, default=0)
    status = db.Column(db.String(50), nullable=False)

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='payrolls', lazy=True)

    # Relationship to PayrollDeduction
    deductions = db.relationship('PayrollDeduction', back_populates='payroll', lazy=True)


class PayrollDeduction(db.Model):
    __tablename__ = "payroll_deduction_tbl"
    payroll_deduction_id = db.Column(db.Integer, primary_key=True)
    payroll_id = db.Column(db.Integer, db.ForeignKey('payroll_tbl.payroll_id'))

    # Government Mandated Contributions
    sss_contribution = db.Column(db.Float, nullable=False, default=0)
    philhealth_contribution = db.Column(db.Float, nullable=False, default=0)
    pagibig_contribution = db.Column(db.Float, nullable=False, default=0)
    withholding_tax = db.Column(db.Float, nullable=False, default=0)
    other_deductions = db.Column(db.Float, nullable=False, default=0)

    # Relationship to Payroll
    payroll = db.relationship('Payroll', back_populates='deductions', lazy=True)


class PayrollContribution(db.Model):
    __tablename__ = "payroll_contribution_tbl"
    payroll_contribution_id = db.Column(db.Integer, primary_key=True)
    sss_contribution = db.Column(db.Float, nullable=False, default=4.5)
    philhealth_contribution = db.Column(db.Float, nullable=False, default=5)
    pagibig_contribution = db.Column(db.Float, nullable=False, default=200)


# Define the Service class
class Service(db.Model):
    __tablename__ = 'service_tbl'
    service_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # in hours
    price = db.Column(db.Float, nullable=False)

    bookings = db.relationship('Booking', back_populates='services', lazy=True)


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
class BillingAdminLogin(db.Model):
    __tablename__ = "billing_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)


class PayrollAdminLogin(db.Model):
    __tablename__ = "payroll_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)


class EmployeeAdminLogin(db.Model):
    __tablename__ = "employee_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)


class CustomerAdminLogin(db.Model):
    __tablename__ = "customer_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)


class InventoryAdminLogin(db.Model):
    __tablename__ = "inventory_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)


class SuperadminLogin(UserMixin, db.Model):
    __tablename__ = "superadmin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)

    # Implement the get_id() method to return the user's id
    def get_id(self):
        return str(self.login_id)

