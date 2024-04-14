from sqlalchemy import Time, UniqueConstraint
from datetime import time
from db import db


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
    total_ot_hrs = db.Column(db.Float, nullable=False)
    total_tardiness = db.Column(db.Float, nullable=False)
    base_salary = db.Column(db.Float, nullable=False)
    gross_pay = db.Column(db.Float, nullable=False)
    net_pay = db.Column(db.Float, nullable=False)
    thirteenth_month_pay = db.Column(db.Float, nullable=True, default=0)
    status = db.Column(db.String(50), nullable=False)

    # Relationship to Employee
    employee = db.relationship('Employee', back_populates='payrolls', lazy=True)

    # Relationship to PayrollDeduction
    deductions = db.relationship('PayrollDeduction', back_populates='payroll', lazy=True)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('employee_id', 'period_start', 'period_end', name='unique_payroll_record'),
    )


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


class PayrollContributionRate(db.Model):
    __tablename__ = "payroll_contribution_rate_tbl"
    payroll_contribution_rate_id = db.Column(db.Integer, primary_key=True)
    sss = db.Column(db.Float, nullable=False, default=4.5)
    philhealth = db.Column(db.Float, nullable=False, default=5)
    pagibig = db.Column(db.Float, nullable=False, default=200)



