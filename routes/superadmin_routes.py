import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, CustomerAdminLogin, BillingAdminLogin, EmployeeAdminLogin, InventoryAdminLogin, PayrollAdminLogin

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
    billing_admin_logins = BillingAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in billing_admin_logins
    ]

    return render_template("billing_tables.html", result=result)


@superadmin_api.post("/superadmin/billing/activate/<int:login_id>")
def activate_billing_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.billing_superadmin"))


@superadmin_api.post("/superadmin/billing/deactivate/<int:login_id>")
def deactivate_billing_account(login_id):
    admin_user = BillingAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.billing_superadmin"))


@superadmin_api.get("/superadmin/customer")
def customer_superadmin():
    customer_admin_logins = CustomerAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in customer_admin_logins
    ]
    return render_template("customer_tables.html", result=result)


@superadmin_api.post("/superadmin/customer/activate/<int:login_id>")
def activate_customer_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.customer_superadmin"))


@superadmin_api.post("/superadmin/customer/deactivate/<int:login_id>")
def deactivate_customer_account(login_id):
    admin_user = CustomerAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.customer_superadmin"))


@superadmin_api.get("/superadmin/employee")
def employee_superadmin():
    employee_admin_logins = EmployeeAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in employee_admin_logins
    ]
    return render_template("employee_tables.html", result=result)


@superadmin_api.post("/superadmin/employee/activate/<int:login_id>")
def activate_employee_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.employee_superadmin"))


@superadmin_api.post("/superadmin/employee/deactivate/<int:login_id>")
def deactivate_employee_account(login_id):
    admin_user = EmployeeAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.employee_superadmin"))


@superadmin_api.get("/superadmin/inventory")
def inventory_superadmin():
    inventory_admin_logins = InventoryAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in inventory_admin_logins
    ]
    return render_template("inventory_tables.html", result=result)


@superadmin_api.post("/superadmin/inventory/activate/<int:login_id>")
def activate_inventory_account(login_id):
    admin_user = InventoryAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.inventory_superadmin"))


@superadmin_api.post("/superadmin/inventory/deactivate/<int:login_id>")
def deactivate_inventory_account(login_id):
    admin_user = InventoryAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.inventory_superadmin"))


@superadmin_api.get("/superadmin/payroll")
def payroll_superadmin():
    payroll_admin_logins = PayrollAdminLogin.query.all()

    # Convert the data to a list of dictionaries for easier JSON serialization
    result = [
        {
            "login_id": entry.login_id,
            "name": entry.name,
            "email": entry.email,
            "role": entry.role,
            "is_active": entry.is_active,
            "email_confirm": entry.email_confirm
        }

        for entry in payroll_admin_logins
    ]

    return render_template("payroll_tables.html", result=result)


@superadmin_api.post("/superadmin/payroll/activate/<int:login_id>")
def activate_payroll_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = True
        db.session.commit()

    return redirect(url_for("superadmin_api.payroll_superadmin"))


@superadmin_api.post("/superadmin/payroll/deactivate/<int:login_id>")
def deactivate_payroll_account(login_id):
    admin_user = PayrollAdminLogin.query.get(login_id)

    if admin_user:
        admin_user.is_active = False
        db.session.commit()

    return redirect(url_for("superadmin_api.payroll_superadmin"))


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






