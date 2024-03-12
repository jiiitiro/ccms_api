import os
from flask import Blueprint, request, jsonify, render_template
from models import db, CustomerAdminLogin
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
import smtplib
from passlib.hash import pbkdf2_sha256


superadmin_api = Blueprint('superadmin_api', __name__)

# superadmin api-key
API_KEY = os.environ.get('SUPERADMIN_API_KEY')


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





