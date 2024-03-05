import os
from flask import Blueprint, request, jsonify
from models import db, CustomerAdminLogin

customer_admin_api = Blueprint('customer_admin_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")


@customer_admin_api.get("/customer/admin-login")
def get_all_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        response_data = db.session.execute(db.select(CustomerAdminLogin)).scalars().all()
        user_data = [
            {
                "login_id": data.login_id,
                "email": data.email,
                "password": data.password,
                "role": data.role,
                "is_active": data.is_active,
            } for data in response_data
        ]
        response = jsonify({"Customer_Admin_Login_Data": user_data})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@customer_admin_api.get("/customer/admin-login/<int:login_id>")
def get_spec_cust_admin_data(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        login_data = db.session.query(CustomerAdminLogin).filter_by(login_id=login_id).first()
        if login_data:
            login_data_dict = {
                "login_id": login_data.login_id,
                "email": login_data.email,
                "password": login_data.password,
                "role": login_data.role,
                "is_active": login_data.is_active,
            }
            response = jsonify({"login_data": login_data_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Customer not found"}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@customer_admin_api.post("/customer/admin-login/register")
def register_customer_admin_login():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            new_login = CustomerAdminLogin(
                email=request.form.get("email"),
                password=request.form.get("password"),
                role=request.form.get("role"),
            )
            db.session.add(new_login)
            db.session.commit()

            new_login_dict = [
                {
                    "login_id": new_login.login_id,
                    "email": new_login.email,
                    "password": new_login.password,
                    "role": new_login.role,
                    "is_active": new_login.is_active,
                }]

            return jsonify(
                success={"message": "Admin/staff added successfully", "customer": new_login_dict}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to add the new admin/staff login. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@customer_admin_api.put("/customer/admin-login/<int:login_id>")
def update_cust_admin_login(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            # Assuming you have a CustomerLogin model
            login_to_update = CustomerAdminLogin.query.filter_by(login_id=login_id).first()

            if login_to_update:
                # Update the login details based on the request data
                login_to_update.email = request.form.get("email")
                login_to_update.password = request.form.get("password")
                login_to_update.role = request.form.get("role")
                # Convert the 'is_active' string to a boolean
                is_active_str = request.form.get("is_active")
                login_to_update.is_active = True if is_active_str.lower() == 'true' else False

                # Commit the changes to the database
                db.session.commit()

                login_to_update_dict = {
                    "login_id": login_to_update.login_id,
                    "email": login_to_update.email,
                    "password": login_to_update.password,
                    "role": login_to_update.role,
                    "is_active": login_to_update.is_active,
                }

                return jsonify(success={"message": "Customer admin login updated successfully",
                                        "login_date": login_to_update_dict}), 200
            else:
                return jsonify(error={"message": "Customer admin login not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update customer admin login. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@customer_admin_api.delete("/customer/admin-login/<int:login_id>")
def delete_cust_admin_login_data(login_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        cust_admin_to_delete = db.session.execute(db.select(CustomerAdminLogin).
                                                  where(CustomerAdminLogin.login_id == login_id)).scalar()
        if cust_admin_to_delete:
            db.session.delete(cust_admin_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted the customer admin login data."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

