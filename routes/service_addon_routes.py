import os
from flask import Blueprint, request, jsonify
from models import ServiceAddon
from db import db

service_addon_api = Blueprint("service_addon_api", __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@service_addon_api.get("/service-addon/all")
def get_all_service_addon_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = ServiceAddon.query.all()

        service_addon_data = [
            {
                "service_addon_id": data.service_addon_id,
                "description": data.description,
                "pricing_description": data.pricing_description,
                "price": data.price
            } for data in query_data
        ]

        return jsonify(success={"service_addon_data": service_addon_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@service_addon_api.get("/service-addon/<int:service_addon_id>")
def get_specific_service_addon(service_addon_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = ServiceAddon.query.filter_by(service_addon_id=service_addon_id).first()

        if query_data is None:
            return jsonify(error={"message": "Service addon id not found."}), 404

        service_addon_data = [
            {
                "service_addon_id": query_data.service_addon_id,
                "description": query_data.description,
                "pricing_description": query_data.pricing_description,
                "price": query_data.price
            }
        ]

        return jsonify(success={"service_addon_data": service_addon_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@service_addon_api.post("/service-addon/add")
def add_service_addon_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        new_service_addon = ServiceAddon(
            description=request.form.get("description"),
            pricing_description=request.form.get("pricing_description"),
            price=request.form.get("price")
        )

        db.session.add(new_service_addon)
        db.session.commit()

        return jsonify(success={"message": "Service addon successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@service_addon_api.delete("/service-addon/delete/<int:service_addon_id>")
def delete_service_addon(service_addon_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = ServiceAddon.query.filter_by(service_addon_id=service_addon_id).first()

        if query_data is None:
            return jsonify(error={"message": "Service addon id not found."}), 404

        db.session.delete(query_data)
        db.session.commit()

        return jsonify(success={"message": "Service addon data successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@service_addon_api.patch("/service-addon/update/<int:service_addon_id>")
def update_service_addon(service_addon_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        service_addon_to_update = ServiceAddon.query.filter_by(service_addon_id=service_addon_id).first()

        if service_addon_to_update is None:
            return jsonify(error={"message": "Service addon id not found."}), 404

        update_data = {
            "description": request.form.get("description", service_addon_to_update.description),
            "pricing_description": request.form.get("pricing_description", service_addon_to_update.pricing_description),
            "price": request.form.get("price", service_addon_to_update.price),
        }

        for key, value in update_data.items():
            setattr(service_addon_to_update, key, value)

        db.session.commit()

        service_addon_dict = {
            "description": service_addon_to_update.description,
            "pricing_description": service_addon_to_update.pricing_description,
            "price": service_addon_to_update.price
        }

        return jsonify(success={"message": "Service addon data updated successfully.",
                                "service_addon_data": service_addon_dict}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


