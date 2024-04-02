from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from models import db, Payroll, Employee, Attendance, PayrollContribution
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import calendar
from datetime import date
from models.ccsms_models import PayrollDeduction

payroll_api = Blueprint('payroll_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")


# Function to generate payroll for employees
def generate_payroll():
    # Get all active employees
    active_employees = Employee.query.filter_by(is_active=True).all()

    # Get payroll contributions
    payroll_contributions = PayrollContribution.query.first()
    sss_contribution_rate = payroll_contributions.sss_contribution
    philhealth_contribution_rate = payroll_contributions.philhealth_contribution
    pagibig_contribution_rate = payroll_contributions.pagibig_contribution

    # Calculate payroll for each employee
    for employee in active_employees:
        # Get the attendances within the period
        attendances_within_period = Attendance.query.filter(
            Attendance.employee_id == employee.employee_id,
            Attendance.work_date.between(get_period_start(), get_period_end())
        ).all()

        # Initialize total days worked
        total_days_worked = 0

        # Calculate total days worked by iterating over attendances
        for attendance in attendances_within_period:
            if attendance.login_time and attendance.logout_time:
                total_days_worked += 1
            elif attendance.login_time and not attendance.logout_time:
                pass

        # Calculate base salary based on total days worked
        base_salary = employee.daily_rate * total_days_worked

        # Calculate gross pay
        gross_pay = base_salary + employee.de_minimis

        withholding_tax = None
        # Deduct contributions based on the period start date
        if employee.period_start.day >= 16:

            sss_contribution = base_salary * (sss_contribution_rate / 100)
            philhealth_contribution = (employee.base_salary * (philhealth_contribution_rate / 100)) / 2
            pagibig_contribution = pagibig_contribution_rate

            # Calculate withholding tax and other deductions (if any)
            withholding_tax = calculate_withholding_tax(gross_pay)

        else:
            sss_contribution = 0
            philhealth_contribution = 0
            pagibig_contribution = 0

        thirteenth_month_pay = thirteenth_month_pay_computation(employee)

        # other_deductions = calculate_other_deductions()

        # Calculate net pay
        net_pay = gross_pay - (sss_contribution + philhealth_contribution + pagibig_contribution +
                               withholding_tax)

        # Create Payroll instance
        payroll = Payroll(
            employee_id=employee.employee_id,
            period_start=get_period_start(),
            period_end=get_period_end(),
            overtime_hours=employee.overtime_hours,
            overtime_pay=employee.overtime_pay,
            allowances=employee.allowances,
            base_salary=base_salary,
            gross_pay=gross_pay,
            net_pay=net_pay,
            thirteenth_month_pay=thirteenth_month_pay,
            status="Calculated"
        )

        # Create Payroll Deduction instance
        deduction = PayrollDeduction(
            payroll_id=payroll.payroll_id,
            sss_contribution=sss_contribution,
            philhealth_contribution=philhealth_contribution,
            pagibig_contribution=pagibig_contribution,
            withholding_tax=withholding_tax,
            other_deductions=0,
        )

        # Associate deduction with payroll
        payroll.deductions.append(deduction)

        db.session.add(payroll)

    db.session.commit()


def calculate_withholding_tax(gross_pay):
    # Tax rates and brackets for 2024
    tax_brackets = [
        (250000, 0.20),
        (400000, 0.25),
        (800000, 0.30),
        (2000000, 0.32),
        (8000000, 0.35),
        (16000000, 0.40),
        (32000000, 0.42),
        (64000000, 0.45),
        (64000000, 0.50)  # For incomes above 64M
    ]

    # Compute withholding tax
    tax_due = 0
    taxable_income = gross_pay * 12  # Annualized gross pay assuming monthly salary

    for i, (threshold, rate) in enumerate(tax_brackets):
        if taxable_income <= threshold:
            tax_due += taxable_income * rate
            break
        else:
            if i == len(tax_brackets) - 1:
                # Apply the highest tax rate for incomes above the highest threshold
                tax_due += (taxable_income - tax_brackets[-1][0]) * tax_brackets[-1][1]
            else:
                # Apply tax rate for this bracket
                tax_due += (threshold - tax_brackets[i - 1][0]) * rate

    # Convert annual tax due to monthly withholding tax
    withholding_tax = tax_due / 12

    return withholding_tax


# Function to calculate other deductions
def calculate_other_deductions():
    # Your logic to calculate other deductions
    pass


# Function to get the start date of the payroll period
def get_period_start():
    today = datetime.now()
    if today.day <= 15:
        return today.replace(day=1)
    else:
        return today.replace(day=16)


# Function to get the end date of the payroll period
def get_period_end():
    today = datetime.now()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    if today.day <= 15:
        return today.replace(day=15)
    else:
        return today.replace(day=last_day_of_month)


def thirteenth_month_pay_computation(employee):

    today = date.today()
    thirteenth_month_pay = 0
    # Check if the current date is December 20th
    if today.month == 12 and today.day == 20:

        # Calculate total basic salary earned during the year
        total_base_salary = calculate_total_base_salary(employee)

        # Calculate thirteenth month pay
        thirteenth_month_pay = total_base_salary / 12

    return thirteenth_month_pay


def calculate_total_base_salary(employee):
    # Get the current year
    current_year = date.today().year

    # Query all the payrolls for the employee within the current year
    payrolls_within_year = Payroll.query.filter_by(employee_id=employee.employee_id) \
        .filter(Payroll.period_start >= date(current_year, 1, 1)) \
        .filter(Payroll.period_end <= date(current_year, 12, 31)) \
        .all()

    # Sum up the base_salary from all the payrolls
    total_basic_salary = sum(payroll.base_salary for payroll in payrolls_within_year)

    return total_basic_salary


# Create a scheduler
scheduler = BackgroundScheduler()

# Add the payroll generation job to run on the 10th and 25th of every month
scheduler.add_job(generate_payroll, 'cron', day='5,20')

# Start the scheduler
scheduler.start()


# Get all payroll table data
@payroll_api.get('/payroll/all')
def payroll_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        payroll_data = db.session.execute(db.select(Payroll)).scalars().all()
        payroll_dict = [{
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
        response = jsonify({"payroll_data": payroll_dict})
        return response, 200

    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@payroll_api.get("/payroll/<int:payroll_id>")
def get_specific_payroll(payroll_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        payroll_data = db.session.query(Payroll).filter_by(payroll_id=payroll_id).first()
        if payroll_data:
            payroll_dict = {
                'payroll_id': payroll_data.payroll_id,
                'employee_id': payroll_data.employee_id,
                'period_start': payroll_data.period_start,
                'period_end': payroll_data.period_end,
                'basic_pay': payroll_data.basic_pay,
                'overtime_hours': payroll_data.overtime_hours,
                'overtime_pay': payroll_data.overtime_pay,
                'allowances': payroll_data.allowances,
                'gross_pay': payroll_data.gross_pay,
                'sss_contribution': payroll_data.sss_contribution,
                'philhealth_contribution': payroll_data.philhealth_contribution,
                'pagibig_contribution': payroll_data.pagibig_contribution,
                'witholding_tax': payroll_data.witholding_tax,
                'other_deduction': payroll_data.other_deduction,
                'net_pay': payroll_data.net_pay,
                'thirteenth_month_pay': payroll_data.thirteenth_month_pay,
                'status': payroll_data.status
            }
            response = jsonify({"payroll": payroll_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Employee not found"}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


