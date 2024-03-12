from flask import jsonify, render_template, request, url_for
import os
import secrets
from passlib.hash import pbkdf2_sha256
import smtplib
from itsdangerous import SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from models import db, Service
from itsdangerous import URLSafeTimedSerializer

service_api = Blueprint('service_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')

# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")

BASE_URL = os.environ.get("BASE_URL")

s = URLSafeTimedSerializer('Thisisasecret!')


@service_api.get("/service/all")
def get_all_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        response_data = db.session.execute(db.select(Service)).scalars().all()
        services_data = [
            {
                "service_id": data.service_id,
                "category": data.category,
                "description": data.description,
                "duration": data.duration,
                "price": data.price,
            } for data in response_data
        ]
        response = jsonify({"services_data": services_data})
        return response, 200
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@service_api.get("/service/<int:service_id>")
def get_specific_data(service_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        service_data = db.session.query(Service).filter_by(service_id=service_id).first()
        if service_data:
            service_dict = {
                "description": service_data.description,
                "category": service_data.category,
                "duration": service_data.duration,
                "price": service_data.price,
            }
            response = jsonify({"service_data": service_dict})
            return response, 200
        else:
            return jsonify(error={"message": "service not found"}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@service_api.post("/service/add")
def add_service():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            new_service = Service(
                description=request.form.get("description"),
                category=request.form.get("category"),
                duration=request.form.get("duration"),
                price=request.form.get("price"),
            )

            db.session.add(new_service)
            db.session.commit()

            new_service_dict = [
                {
                    "description": new_service.description,
                    "category": new_service.category,
                    "duration": new_service.duration,
                    "price": new_service.price,
                }
            ]

            return jsonify(success={"message": "Service successfully added", "customer": new_service_dict}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"Message": f"Failed to add service. Error: {str(e)}"}), 500
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@service_api.delete("/service/delete/<int:service_id>")
def delete_data(service_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        service_to_delete = db.session.execute(db.select(Service).where(Service.service_id == service_id)).scalar()
        if service_to_delete:
            db.session.delete(service_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted a service."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@service_api.patch("/service/update/<int:service_id>")
def update_service(service_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        try:
            service_to_update = Service.query.filter_by(service_id=service_id).first()

            if service_to_update:
                # Get the fields to update from the form data
                update_data = {'description': request.form.get('description', service_to_update.description),
                               'category': request.form.get('category', service_to_update.category),
                               'duration': request.form.get('duration', service_to_update.duration),
                               'price': request.form.get('price', service_to_update.price)}

                # Update the customer fields
                for key, value in update_data.items():
                    setattr(service_to_update, key, value)

                db.session.commit()

                service_dict = {
                    "description": service_to_update.description,
                    "category": service_to_update.category,
                    "duration": service_to_update.duration,
                    "price": service_to_update.price,
                }

                return jsonify(success={"message": "Service data updated successfully",
                                        "service_data": service_dict}), 200
            else:
                return jsonify(error={"message": "Customer not found"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify(error={"message": f"Failed to update customer data. Error: {str(e)}"}), 500
    else:
        return jsonify(error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403
