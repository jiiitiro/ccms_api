from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from models import db, Payroll, Employee
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import calendar

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

    # Calculate payroll for each employee
    for employee in active_employees:
        # Calculate deductions
        sss_contribution = employee.base_salary * 4.5
        philhealth_contribution = (employee.base_salary * 0.05) / 2
        pagibig_contribution = 200

        # Calculate gross pay
        gross_pay = employee.base_salary + employee.overtime_pay + employee.allowances

        # Calculate withholding tax and other deductions (if any)
        withholding_tax = calculate_withholding_tax(gross_pay)
        other_deductions = calculate_other_deductions()

        # Calculate net pay
        net_pay = gross_pay - (sss_contribution + philhealth_contribution + pagibig_contribution +
                               withholding_tax + other_deductions)

        # Create Payroll object
        payroll = Payroll(
            employee_id=employee.employee_id,
            period_start=get_period_start(),
            period_end=get_period_end(),
            overtime_hours=employee.overtime_hours,
            overtime_pay=employee.overtime_pay,
            allowances=employee.allowances,
            gross_pay=gross_pay,
            sss_contribution=sss_contribution,
            philhealth_contribution=philhealth_contribution,
            pagibig_contribution=pagibig_contribution,
            withholding_tax=withholding_tax,
            other_deductions=other_deductions,
            net_pay=net_pay,
            status="Pending"  # Or any other appropriate status
        )

        db.session.add(payroll)

    db.session.commit()


# Function to calculate withholding tax
def calculate_withholding_tax(gross_pay):
    # Your logic to calculate withholding tax
    pass


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
