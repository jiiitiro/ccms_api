import os
from flask import Blueprint, request, jsonify
from models import Service, ServiceAddon
from models.activity_logs_models import BillingAdminActivityLogs
from db import db
import logging
from functions import log_activity
from datetime import datetime

logging.basicConfig(level=logging.INFO)

service_api = Blueprint('service_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@service_api.get("/service/all")
def get_all_data():
    api_key_header = request.headers.get("x-api-key")

    if api_key_header == API_KEY:
        response_data = db.session.execute(db.select(Service)).scalars().all()

        response_service_addons = ServiceAddon.query.all()

        services_data = []
        property_size = []
        service_addons = []

        for data in response_data:
            service = {
                "service_id": data.service_id,
                "category": data.category,
                "description": data.description,
                "price": data.price,
            }

            services_data.append(service)

            for data1 in data.property_size_pricing:
                property1 = {
                    "service_id": data.service_id,
                    "property_size_pricing_id": data1.property_size_pricing_id,
                    "property_size": data1.property_size,
                    "pricing": data1.pricing,
                    "add_price_per_floor": data1.add_price_per_floor,
                }

                property_size.append(property1)

        for data3 in response_service_addons:
            service_addon = {
                "service_addon_id": data3.service_addon_id,
                "description": data3.description,
                "pricing_description": data3.pricing_description,
                "price": data3.price
            }

            service_addons.append(service_addon)

        response = jsonify({"services_data": services_data, "property_sizes": property_size,
                            "service_addons": service_addons})

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
                "service_id": service_data.service_id,
                "category": service_data.category,
                "description": service_data.description,
                "price": service_data.price,
                "property_sizes": [
                    {
                        "property_size_pricing_id": data.property_size_pricing_id,
                        "property_size": data.property_size,
                        "pricing": data.pricing,
                        "add_price_per_floor": data.add_price_per_floor,
                    } for data in service_data.property_size_pricing
                ]
            }

            response = jsonify({"service_data": service_dict})
            return response, 200
        else:
            return jsonify(error={"message": "Service id not found."}), 404
    else:
        return jsonify(
            error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@service_api.post("/service/add")
def add_service():

    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403

        new_service = Service(
            description=request.form.get("description"),
            category=request.form.get("category"),
            price=request.form.get("price")
        )

        db.session.add(new_service)
        db.session.commit()

        new_service_dict = {
            "service_id": new_service.service_id,
            "description": new_service.description,
            "category": new_service.category,
            "price": new_service.price
        }

        log_activity(
            BillingAdminActivityLogs,
            login_id=request.form.get("login_id"),
            logs_description=f"Add service with an id of {new_service.service_id}"
        )

        return jsonify(success={"message": "Service successfully added", "service": new_service_dict}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"Message": f"Failed to add service. Error: {str(e)}"}), 500


@service_api.delete("/service/delete/<int:service_id>")
def delete_data(service_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        service_to_delete = Service.query.filter_by(service_id=service_id).first()
        if service_to_delete:

            try:
                db.session.delete(service_to_delete)
                db.session.commit()

                log_activity(
                    BillingAdminActivityLogs, login_id=request.form.get("login_id"),
                    logs_description=f"Delete service with an id of {service_id}"
                )

            except Exception as e:
                db.session.rollback()
                return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500

            return jsonify(success={"message": "Successfully deleted a service."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a data with that id was not found in the database."}), 404
    else:
        return jsonify(error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403


@service_api.post("/service/update/<int:service_id>")
def update_service(service_id):
    api_key_header = request.headers.get("x-api-key")

    if api_key_header != API_KEY:
        logging.warning("Invalid API key")
        return jsonify(error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403

    try:
        service_to_update = Service.query.filter_by(service_id=service_id).first()

        if service_to_update:
            # Get the fields to update from the form data
            update_data = {
                'description': request.form.get('description', service_to_update.description),
                'category': request.form.get('category', service_to_update.category),
                'price': request.form.get('price', service_to_update.price),
            }

            # Update the service fields
            for key, value in update_data.items():
                setattr(service_to_update, key, value)

            db.session.commit()

            log_activity(
                BillingAdminActivityLogs, login_id=request.form.get("login_id"),
                logs_description=f"Update service with an id of {service_id}"
            )

            return jsonify(success={"message": "Service data updated successfully.", "update_data": update_data}), 200
        else:
            return jsonify(error={"message": "Service id not found"}), 404

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to update service. Error: {str(e)}")
        return jsonify(error={"message": f"Failed to update service. Error: {str(e)}"}), 500