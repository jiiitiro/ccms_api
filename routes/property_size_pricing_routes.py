import os
from flask import Blueprint, request, jsonify
from models import Service, PropertySizePricing
from db import db

# api-key
API_KEY = os.environ.get('API_KEY')

property_size_pricing_api = Blueprint('property_size_pricing_api', __name__)


@property_size_pricing_api.get("/property-size-pricing/all")
def get_all_property_size_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403

        query_data = PropertySizePricing.query.all()

        property_size_pricing_data = [
            {
                "property_size_pricing_id": data.property_size_pricing_id,
                "service_id": data.service_id,
                "service_category": data.services.category,
                "property_size": data.property_size,
                "pricing": data.pricing,
                "add_price_per_floor": data.add_price_per_floor
            } for data in query_data
        ]

        return jsonify(success={"property_size_pricing_data":property_size_pricing_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@property_size_pricing_api.post("/property-size-pricing/add")
def add_property_size_pricing():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403

        query_service_id = Service.query.filter_by(service_id=request.form.get("service_id")).first()

        if query_service_id is None:
            return jsonify(error={"message": "Service id not found."}), 403

        new_data = PropertySizePricing(
            service_id=request.form.get("service_id"),
            property_size=request.form.get("property_size"),
            pricing=float(request.form.get("pricing")),
            add_price_per_floor=float(request.form.get("add_price_per_floor"))
        )

        db.session.add(new_data)
        db.session.commit()

        return jsonify(success={"message": "Property size pricing successfully added."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@property_size_pricing_api.patch("/property-size-pricing/update/<int:property_size_pricing_id>")
def update_property_size_pricing(property_size_pricing_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"message": "Not Authorized", "details": "Make sure you have the correct api_key."}), 403

        query_data = PropertySizePricing.query.filter_by(property_size_pricing_id=property_size_pricing_id).first()

        if query_data is None:
            return jsonify(error={"message": "Property size pricing id not found."}), 403

        query_data.service_id = request.form.get("service_id", query_data.service_id)
        query_data.property_size = request.form.get("property_size", query_data.property_size)
        query_data.pricing = request.form.get("pricing", query_data.pricing)
        query_data.pricing = request.form.get("")

        db.session.commit()

        return jsonify(success={"message": "Successfully updated the property size pricing data."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500

