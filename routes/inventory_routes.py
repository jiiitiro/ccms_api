import os
from flask import Blueprint, request, jsonify
from models import Employee, Attendance, Schedule, Inventory, Supplier
from db import db


inventory_api = Blueprint('inventory_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@inventory_api.get("/inventory/all")
def get_all_inventory_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        query_data = Inventory.query.all()
        try:
            inventory_data = [
                {
                    "inventory_id": data.inventory_id,
                    "supplier_id": data.supplier_id,
                    "category": data.category,
                    "item_name": data.item_name,
                    "available_stock": data.available_stock,
                    "used_item": data.used_item,
                    "reorder_level": data.reorder_level,
                    "item_status": data.item_status,
                    "unit_price": data.unit_price
                } for data in query_data
            ]
            return jsonify({"inventory_data": inventory_data}), 200
        except Exception as e:
            # Return error response if any exception occurs
            return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@inventory_api.get("/inventory/<int:inventory_id>")
def get_specific_inventory_data(inventory_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        # Query the inventory data by ID
        inventory_data = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if inventory_data:
            inventory_data_dict = [
                {
                    "inventory_id": inventory_data.inventory_id,
                    "supplier_id": inventory_data.supplier_id,
                    "category": inventory_data.category,
                    "item_name": inventory_data.item_name,
                    "available_stock": inventory_data.available_stock,
                    "used_item": inventory_data.used_item,
                    "reorder_level": inventory_data.reorder_level,
                    "item_status": inventory_data.item_status,
                    "unit_price": inventory_data.unit_price
                }
            ]

            return jsonify({"inventory_data": inventory_data_dict}), 200
        else:
            return jsonify(error={"message": "Inventory ID not found."}), 404
    except Exception as e:
        # Return error response if any exception occurs
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@inventory_api.post("/inventory/add")
def add_item_with_supplier():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        # if there is a supplier id
        if request.form.get("supplier_id"):

            supplier_id = int(request.form.get("supplier_id"))

            supplier_query = Supplier.query.filter_by(supplier_id=supplier_id).first()

            if supplier_query is None:
                return jsonify(error={"message": "Supplier ID not found."}), 404

            new_inventory = Inventory(
                supplier_id=supplier_query.supplier_id,
                category=request.form.get("category"),
                item_name=request.form.get("item_name"),
                available_stock=int(request.form.get("available_stock")),
                reorder_level=int(request.form.get("reorder_level")),
                item_status="Available",
                unit_price=float(request.form.get("unit_price"))
            )
        # if there is no supplier
        else:
            new_inventory = Inventory(
                category=request.form.get("category"),
                item_name=request.form.get("item_name"),
                available_stock=request.form.get("available_stock"),
                reorder_level=request.form.get("reorder_level"),
                item_status="Available",
                unit_price=float(request.form.get("unit_price"))
            )

        db.session.add(new_inventory)

        db.session.commit()

        return jsonify(success={"message": "Inventory item successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@inventory_api.delete("/inventory/delete/<int:inventory_id>")
def delete_inventory_data(inventory_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if query_data is None:
            return jsonify(error={"message": "Inventory Id not found."}), 404

        db.session.delete(query_data)
        db.session.commit()

        return jsonify(success={"message": "Successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@inventory_api.patch("/inventory/update/<int:inventory_id>")
def update_inventory_data(inventory_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if query_data is None:
            return jsonify(error={"message": "Inventory id not found."}), 404

        if request.form.get("supplier_id"):
            supplier_id = int(request.form.get("supplier_id"))
            supplier_query = Supplier.query.filter_by(supplier_id=supplier_id).first()
            if not supplier_query:
                return jsonify(error={"message": "Supplier id not found."}), 404

        # Update inventory data based on the request
        query_data.supplier_id = request.form.get("supplier_id", query_data.supplier_id)
        query_data.category = request.form.get("category", query_data.category)
        query_data.item_name = request.form.get("item_name", query_data.item_name)
        query_data.reorder_level = request.form.get("reorder_level", query_data.reorder_level)
        query_data.unit_price = float(request.form.get("unit_price", query_data.unit_price))

        if request.form.get("used_item") and request.form.get("available_stock"):
            query_data.used_item += int(request.form.get("used_item"))
            available_stock = query_data.available_stock + int(request.form.get("available_stock"))
            query_data.available_stock = available_stock - int(request.form.get("used_item"))
        elif request.form.get("available_stock") and not request.form.get("used_item"):
            query_data.available_stock += int(request.form.get("available_stock"))
        elif not request.form.get("available_stock") and request.form.get("used_item"):
            query_data.available_stock -= int(request.form.get("used_item"))
            query_data.used_item += int(request.form.get("used_item"))

        # query_data.available_stock = request.form.get("available_stock", query_data.available_stock)

        # Reevaluate item_status
        if int(query_data.available_stock) <= 0:
            query_data.item_status = "Not Available"
        elif int(query_data.available_stock) <= int(query_data.reorder_level):
            query_data.item_status = "Restock"
        else:
            query_data.item_status = "Available"

        db.session.commit()

        return jsonify(success={"message": "Inventory data updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500




