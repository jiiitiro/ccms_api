import os
from flask import Blueprint, request, jsonify, render_template
from models import db, CustomerAdminLogin, BillingAdminLogin, EmployeeAdminLogin, InventoryAdminLogin, PayrollAdminLogin
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
import smtplib
from passlib.hash import pbkdf2_sha256


superadmin_api = Blueprint('superadmin_api', __name__)

# superadmin api-key
API_KEY = os.environ.get('SUPERADMIN_API_KEY')


@superadmin_api.get("/superadmin/login")
def login_superadmin():
    return render_template("superadmin_login.html")


@superadmin_api.get("/superadmin/dashboard")
def dashboard_superadmin():
    return render_template("superadmin_dashboard.html")


@superadmin_api.get("/superadmin/billing")
def billing_superadmin():
    return render_template("billing_tables.html")


@superadmin_api.get("/superadmin/customer")
def customer_superadmin():
    return render_template("customer_tables.html")


@superadmin_api.get("/superadmin/employee")
def employee_superadmin():
    return render_template("employee_tables.html")


@superadmin_api.get("/superadmin/inventory")
def inventory_superadmin():
    return render_template("inventory_tables.html")


@superadmin_api.get("/superadmin/payroll")
def payroll_superadmin():
    return render_template("payroll_tables.html")




@superadmin_api.post("/superadmin/customer-admin/activate/<int:login_id>")
def activate_customer_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/customer-admin/deactivate/<int:login_id>")
def deactivate_customer_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/billing-admin/activate/<int:login_id>")
def activate_billing_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = BillingAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/billing-admin/deactivate/<int:login_id>")
def deactivate_billing_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = BillingAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/employee-admin/activate/<int:login_id>")
def activate_employee_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = EmployeeAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/inventory-admin/activate/<int:login_id>")
def activate_inventory_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/inventory-admin/deactivate/<int:login_id>")
def deactivate_inventory_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = InventoryAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/payroll-admin/activate/<int:login_id>")
def activate_payroll_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = PayrollAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = True
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is activated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@superadmin_api.post("/superadmin/payroll-admin/deactivate/<int:login_id>")
def deactivate_payroll_admin(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        # Find the customer with the confirmed email
        user_ = PayrollAdminLogin.query.filter_by(login_id=login_id).first()

        if user_:
            # Update the email_confirm status to True
            user_.is_active = False
            db.session.commit()

            return jsonify(success={"Message": f" The email {user_.email} is deactivated successfully."})
        else:
            return jsonify(error={"Message": "User not found."}), 404
    else:
        return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403






