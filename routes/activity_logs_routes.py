import os
from flask import Blueprint, request, jsonify
from models.activity_logs_models import (AttendanceAdminActivityLogs, PayrollAdminActivityLogs,
                                         InventoryAdminActivityLogs, EmployeeAdminActivityLogs,
                                         CustomerAdminActivityLogs, BillingAdminActivityLogs)

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

        payroll_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "admin_name": log.payroll_admin.name,
            "logs_description": log.logs_description,
            "log_date": log.log_date
        } for log in query_attendance_logs]

        return jsonify(success={"payroll_activity_logs": payroll_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500


@activity_logs_api.get("/logs/inventory")
def get_all_inventory_logs():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_attendance_logs = InventoryAdminActivityLogs.query.all()

        inventory_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "admin_name": log.payroll_admin.name,
            "logs_description": log.logs_description,
            "log_date": log.log_date
        } for log in query_attendance_logs]

        return jsonify(success={"inventory_activity_logs": inventory_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500


@activity_logs_api.get("/logs/employee")
def get_all_employee_logs():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_attendance_logs = EmployeeAdminActivityLogs.query.all()

        employee_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "admin_name": log.payroll_admin.name,
            "logs_description": log.logs_description,
            "log_date": log.log_date
        } for log in query_attendance_logs]

        return jsonify(success={"employee_activity_logs": employee_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500


@activity_logs_api.get("/logs/customer")
def get_all_customer_logs():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_attendance_logs = CustomerAdminActivityLogs.query.all()

        customer_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "admin_name": log.payroll_admin.name,
            "logs_description": log.logs_description,
            "log_date": log.log_date
        } for log in query_attendance_logs]

        return jsonify(success={"customer_activity_logs": customer_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500


@activity_logs_api.get("/logs/billing")
def get_all_billing_logs():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_attendance_logs = BillingAdminActivityLogs.query.all()

        billing_logs_data = [{
            "log_id": log.log_id,
            "login_id": log.login_id,
            "admin_name": log.payroll_admin.name,
            "logs_description": log.logs_description,
            "log_date": log.log_date
        } for log in query_attendance_logs]

        return jsonify(success={"billing_activity_logs": billing_logs_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"{str(e)}"}), 500



