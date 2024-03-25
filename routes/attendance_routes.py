from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify

from forms import ChangePasswordForm
from models import db, Employee, Attendance
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime

attendance_api = Blueprint('attendance_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@attendance_api.post("/attendance")
def get_attendance():
    try:
        employee = Employee.query.filter(Employee.email == request.form.get("email")).first()

        if not employee:
            return jsonify(error={"message": "Email doesn't exists in the database. "
                                             "Please use a registered email address."}), 400

        if not employee.email_confirm:
            return jsonify(error={"message": "Confirm your email before logging in."}), 401

        if not employee.is_active:
            return jsonify(error={"message": "Account has been deactivated. Please email as at "
                                             "www.busyhands_cleaningservices.manpower@gmail.com"}), 401

        if employee and pbkdf2_sha256.verify(request.form.get("password"), employee.password):
            # Check if employee is already logged in
            existing_attendance = Attendance.query.filter_by(employee_id=employee.employee_id,
                                                             work_date=datetime.now().date()).first()

            if existing_attendance:
                # Employee already has login and logout for today.
                if existing_attendance.login_time and existing_attendance.logout_time:
                    return jsonify(error={"message": "Employee is already logged in and out for today."}), 401

                # Employee is already logged in, so log them out
                existing_attendance.logout_time = datetime.now()
                existing_attendance.logout_status = "Logged Out"

            else:
                # Employee is not logged in, so log them in
                login_time = datetime.now()
                attendance = Attendance(employee_id=employee.employee_id, work_date=login_time.date(),
                                        login_time=login_time, login_status="Logged In")
                db.session.add(attendance)

            db.session.commit()

            return jsonify(success={"message": "Attendance saved."}), 200

        return jsonify(error={"message": "Invalid credentials."}), 401

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"Message": f"Failed to login. Error: {str(e)}"}), 500


@attendance_api.get("/attendance/all")
def get_all_attendance_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Query employees and their attendance data
        query = db.session.query(Employee, Attendance).outerjoin(Attendance, Employee.employee_id == Attendance.employee_id).all()

        # Organize data into a dictionary
        attendance_data = {}
        for employee, attendance in query:
            if employee.employee_id not in attendance_data:
                attendance_data[employee.employee_id] = {
                    "employee_id": employee.employee_id,
                    "first_name": employee.first_name,
                    "middle_name": employee.middle_name,
                    "last_name": employee.last_name,
                    "attendance": []
                }

            if attendance:
                attendance_data[employee.employee_id]["attendance"].append({
                    "attendance_id": attendance.attendance_id,
                    "work_date": attendance.work_date,
                    "login_time": attendance.login_time,
                    "logout_time": attendance.logout_time,
                    "login_status": attendance.login_status,
                    "logout_status": attendance.logout_status
                })

        # Convert dictionary to list
        attendance_list = list(attendance_data.values())

        response = jsonify({"employees": attendance_list})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@attendance_api.get("/attendance/<int:employee_id>")
def get_specific_attendance_employee(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Query employee and their attendance data
        employee = Employee.query.filter_by(employee_id=employee_id).first()

        if not employee:
            return jsonify(error={"message": "Employee not found."}), 404

        attendance_data = Attendance.query.filter_by(employee_id=employee_id).all()

        # Organize attendance data into a list
        attendance_list = []
        for attendance in attendance_data:
            attendance_list.append({
                "attendance_id": attendance.attendance_id,
                "work_date": attendance.work_date,
                "login_time": attendance.login_time,
                "logout_time": attendance.logout_time,
                "login_status": attendance.login_status,
                "logout_status": attendance.logout_status
            })

        response = jsonify({
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "middle_name": employee.middle_name,
            "last_name": employee.last_name,
            "attendance": attendance_list
        })

        return response, 200
    else:
        return jsonify(error={"message": "Not Authorized. Make sure you have the correct api_key."}), 403

