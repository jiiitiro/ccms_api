from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from models import db, Payroll
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from app import BASE_URL

payroll_api = Blueprint('payroll_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")


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
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


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
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


