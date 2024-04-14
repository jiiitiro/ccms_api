import os
from passlib.hash import pbkdf2_sha256
from flask import Blueprint, request, jsonify
from models import Employee, Attendance, Schedule
from db import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

attendance_api = Blueprint('attendance_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


def parse_datetime(datetime_str):
    if datetime_str:
        return datetime.strptime(datetime_str, '%a, %d %b %Y %H:%M:%S %Z')
    else:
        return None


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
                                             "www.busyhands.cleaningservices2024@gmail.com"}), 401

        if employee and pbkdf2_sha256.verify(request.form.get("password"), employee.password):
            # Check if employee is already logged in
            existing_attendance = Attendance.query.filter_by(employee_id=employee.employee_id,
                                                             work_date=datetime.now().date()).first()

            status = None
            if existing_attendance:
                # Employee already has login and logout for today.
                if existing_attendance.login_time and existing_attendance.logout_time:
                    return jsonify(error={"message": "Employee is already logged in and out for today."}), 401

                status = "logout"
                # Employee is already logged in, so log them out
                existing_attendance.logout_time = datetime.now()

                # Determine logout_status based on employee's schedule and logout_time
                schedule = Schedule.query.filter_by(employee_id=employee.employee_id).first()
                end_time = datetime.combine(datetime.today(), schedule.end_time)
                logout_time = datetime.combine(datetime.today(), existing_attendance.logout_time.time())
                if logout_time < end_time:
                    existing_attendance.logout_status = "Early-Out"
                else:
                    existing_attendance.logout_status = "On-Time"

                # Compute the tardiness based on the difference of Employee's schedule start_time and login_time
                start_time = datetime.combine(datetime.today(), schedule.start_time)
                login_time = datetime.combine(datetime.today(), existing_attendance.login_time.time())
                tardiness_delta = login_time - start_time

                existing_attendance.tardiness = max(0, tardiness_delta.total_seconds() // 60)

                # Compute the ot_hrs based on the difference of Employee's schedule end_time and logout_time
                end_time = datetime.combine(datetime.today(), schedule.end_time)
                logout_time = datetime.combine(datetime.today(), existing_attendance.logout_time.time())
                ot_delta = logout_time - end_time

                existing_attendance.ot_hrs = max(0, (ot_delta.total_seconds() + 59) // 3600)  # Round up to the nearest hour

            else:
                status = "login"
                # Employee is not logged in, so log them in
                login_time = datetime.now()
                attendance = Attendance(employee_id=employee.employee_id, work_date=login_time.date(),
                                        login_time=login_time)

                # Determine login_status based on employee's schedule and login_time
                schedule = Schedule.query.filter_by(employee_id=employee.employee_id).first()
                start_time = datetime.combine(datetime.today(), schedule.start_time)
                if login_time > start_time:
                    attendance.login_status = "Late"
                else:
                    attendance.login_status = "On-Time"

                db.session.add(attendance)

            db.session.commit()

            return jsonify(success={"message": f"Hello {employee.first_name}, "
                                               f"your attendance {status} was successfully saved."}), 200

        return jsonify(error={"message": "Invalid credentials."}), 401

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"Message": f"Failed to login. Error: {str(e)}"}), 500


@attendance_api.get("/attendance/all")
def get_all_attendance_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:

        # Query employees, their attendance data, and schedules
        query = db.session.query(Employee, Attendance, Schedule).outerjoin(
            Attendance, Employee.employee_id == Attendance.employee_id).outerjoin(
            Schedule, Employee.employee_id == Schedule.employee_id).all()

        # Organize data into a dictionary
        attendance_data = {}
        for employee, attendance, schedule in query:
            if employee.employee_id not in attendance_data:
                attendance_data[employee.employee_id] = {
                    "employee_id": employee.employee_id,
                    "first_name": employee.first_name,
                    "middle_name": employee.middle_name,
                    "last_name": employee.last_name,
                    "email": employee.email,
                    "position": employee.position,
                    "attendance": [],
                    "schedule": {
                        "start_time": schedule.start_time.strftime("%H:%M:%S") if schedule else None,
                        "end_time": schedule.end_time.strftime("%H:%M:%S") if schedule else None,
                        "day_off": schedule.day_off if schedule else None
                    }
                }

            if attendance:
                attendance_data[employee.employee_id]["attendance"].append({
                    "attendance_id": attendance.attendance_id,
                    "work_date": attendance.work_date,
                    "login_time": attendance.login_time,
                    "logout_time": attendance.logout_time,
                    "login_status": attendance.login_status,
                    "logout_status": attendance.logout_status,
                    "tardiness": attendance.tardiness,
                    "ot_hrs": attendance.ot_hrs
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

        attendance_data = Attendance.query.filter_by(employee_id=employee.employee_id).all()

        # Organize attendance data into a list
        attendance_list = []
        for attendance in attendance_data:
            attendance_list.append({
                "attendance_id": attendance.attendance_id,
                "work_date": attendance.work_date,
                "login_time": attendance.login_time,
                "logout_time": attendance.logout_time,
                "login_status": attendance.login_status,
                "logout_status": attendance.logout_status,
                "tardiness": attendance.tardiness,
                "ot_hrs": attendance.ot_hrs
            })

        # Get the employee's schedule
        employee_schedule = Schedule.query.filter_by(employee_id=employee.employee_id).first()

        # Organize schedule data
        schedule_data = {
            "start_time": employee_schedule.start_time.strftime("%H:%M:%S") if employee_schedule else None,
            "end_time": employee_schedule.end_time.strftime("%H:%M:%S") if employee_schedule else None,
            "day_off": employee_schedule.day_off if employee_schedule else None
        }

        response = jsonify({
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "middle_name": employee.middle_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "position": employee.position,
            "attendance": attendance_list,
            "schedule": schedule_data
        })

        return response, 200
    else:
        return jsonify(error={"message": "Not Authorized. Make sure you have the correct api_key."}), 403


@attendance_api.delete("/attendance/delete/<int:attendance_id>")
def delete_attendance_by_id(attendance_id):
    try:
        query_data = Attendance.query.filter_by(attendance_id=attendance_id).first()

        if query_data is None:
            return jsonify(error={"message": "Attendance id not found."}), 404

        db.session.delete(query_data)
        db.session.commit()

        return jsonify(success={"message": "Successfully delete the attendance data."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 403


@attendance_api.patch("/attendance/update/<int:attendance_id>")
def update_attendance_by_id(attendance_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:

            # Query the attendance record to update
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                return jsonify(error={"message": "Attendance with that id NOT found."}), 404

            # Initialize attendance updates
            attendance_updates = {
                "login_time": parse_datetime(request.form.get("login_time")) or attendance.login_time,
                "logout_time": parse_datetime(request.form.get("logout_time")) or attendance.logout_time,
                "work_date": parse_datetime(request.form.get("work_date")) or attendance.work_date,
                "login_status": request.form.get("login_status", attendance.login_status),
                "logout_status": request.form.get("logout_status", attendance.logout_status),
                "ot_hrs": request.form.get("ot_hrs", attendance.ot_hrs),
                "tardiness": request.form.get("tardiness", attendance.tardiness)
            }

            # Update the attendance record attributes
            for key, value in attendance_updates.items():
                setattr(attendance, key, value)

            # Commit the changes to the database
            db.session.commit()

            return jsonify(success={"message": "Attendance record updated successfully."}), 200
        except IntegrityError:
            # Rollback the transaction in case of integrity error
            db.session.rollback()
            return jsonify(error={"message": "Integrity error occurred."}), 500
    else:
        return jsonify(error={"message": "Not Authorized. Make sure you have the correct api_key."}), 403

