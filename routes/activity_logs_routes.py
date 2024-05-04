import os
from flask import Blueprint, request, jsonify
from models.activity_logs_models import AttendanceAdminActivityLogs, PayrollAdminActivityLogs

activity_logs_api = Blueprint("activity_logs_api", __name__)

API_KEY = os.environ.get("API_KEY")


@activity_logs_api.get("/logs/attendance")
def get_all_attendance_logs():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_attendance_logs = AttendanceAdminActivityLogs.query.all()

        attendance_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "employee_name": f"{log.employee.first_name} {log.employee.last_name}",
            "logs_description": log.logs_description,
            "log_date": log.log_date,
            "log_location": log.log_location
        } for log in query_attendance_logs]

        return jsonify(success={"attendance_activity_logs": attendance_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500


@activity_logs_api.get("/logs/payroll")
def get_all_payroll_logs():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_attendance_logs = PayrollAdminActivityLogs.query.all()

        attendance_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "admin_name": log.payroll_admin.name,
            "logs_description": log.logs_description,
            "log_date": log.log_date
        } for log in query_attendance_logs]

        return jsonify(success={"payroll_activity_logs": attendance_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500


