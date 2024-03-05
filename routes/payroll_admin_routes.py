import os
from flask import Blueprint, request, jsonify
from models import db, PayrollAdminLogin

payroll_admin_api = Blueprint('payroll_admin_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")


# payroll admin-login
@payroll_admin_api.get("/payroll/admin-login")
def get_all_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        response_data = db.session.execute(db.select(PayrollAdminLogin)).scalars().all()
        user_data = [
            {
                "login_id": data.login_id,
                "email": data.email,
                "password": data.password,
                "role": data.role,
                "is_active": data.is_active,
            } for data in response_data
        ]
        response = jsonify({"Payroll_Admin_Login_Data": user_data})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# Get all payroll_login_tbl data
@payroll_admin_api.route("/payroll_login")
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

