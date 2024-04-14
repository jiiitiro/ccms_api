import os
from flask import Blueprint, request, jsonify
from models import Supplier
from db import db

supplier_api = Blueprint('supplier_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@supplier_api.get("/supplier/all")
def get_all_supplier_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Supplier.query.all()

        supplier_data = [
            {
                "supplier_id": data.supplier_id,
                "supplier_name": data.supplier_name,
                "contact_person": data.contact_person,
                "email": data.email,
                "phone": data.phone,
                "address": data.supplier_id
            } for data in query_data
        ]

        return jsonify(success={"supplier_data": supplier_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@supplier_api.get("/supplier/<int:supplier_id>")
def get_specific_supplier(supplier_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Supplier.query.filter_by(supplier_id=supplier_id).first()

        if query_data is None:
            return jsonify(error={"message": "supplier id not found."}), 404

        supplier_data = [
            {
                "supplier_id": query_data.supplier_id,
                "supplier_name": query_data.supplier_name,
                "contact_person": query_data.contact_person,
                "email": query_data.email,
                "phone": query_data.phone,
                "address": query_data.supplier_id
            }
        ]

        return jsonify(success={"supplier_data": supplier_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@supplier_api.post("/supplier/add")
def add_supplier():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        new_supplier = Supplier(
            supplier_name=request.form.get("supplier_name"),
            contact_person=request.form.get("contact_person"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            address=request.form.get("address")
        )

        db.session.add(new_supplier)
        db.session.commit()

        return jsonify(success={"message": "Supplier successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@supplier_api.patch("/supplier/update/<int:supplier_id>")
def update_supplier_data(supplier_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Supplier.query.filter_by(supplier_id=supplier_id).first()

        if query_data is None:
            return jsonify(error={"message": "Supplier id not found."}), 404

        # Extract data from the request and update the query_data object
        query_data.supplier_name = request.form.get("supplier_name", query_data.supplier_name)
        query_data.contact_person = request.form.get("contact_person", query_data.contact_person)
        query_data.email = request.form.get("email", query_data.email)
        query_data.phone = request.form.get("phone", query_data.phone)
        query_data.address = request.form.get("address", query_data.address)

        # Commit the changes to the database
        db.session.commit()

        return jsonify(success={"message": "Supplier data updated successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500
