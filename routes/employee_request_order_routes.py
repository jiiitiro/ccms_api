import os
from db import db
from flask import Blueprint, request, jsonify
from models import EmployeeRequestOrder, Employee, Inventory
from datetime import datetime

from models.inventory_models import EmployeeRequestInventoryAssociation

employee_request_api = Blueprint("employee_request_api", __name__)

API_KEY = os.environ.get("API_KEY")


@employee_request_api.post("/employee-request-order/add")
def add_employee_request_order():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_employee = Employee.query.filter_by(employee_id=request.form.get("employee_id")).first()

        if query_employee is None:
            return jsonify(error={"message": "Employee id not found."}), 404

        inventory_ids = [int(_id.strip()) for _id in request.form.get("inventory_id").split(',')]

        # Query inventory items based on the list of inventory_ids
        query_inventory = Inventory.query.filter(Inventory.inventory_id.in_(inventory_ids)).all()

        # Check if any inventory items were not found
        not_found_ids = set(inventory_ids) - {inventory.inventory_id for inventory in query_inventory}
        if not_found_ids:
            return jsonify(error={"message": f"Inventory IDs not found: {', '.join(map(str, not_found_ids))}"}), 404

        # item_quantities = [int(qty.strip()) for qty in request.form.get("item_qty").split(',')]

        new_employee_request_order = EmployeeRequestOrder(
            employee_id=request.form.get("employee_id"),
            order_date=datetime.now()
        )

        for inventory_id in zip(inventory_ids):
            new_association = EmployeeRequestInventoryAssociation(
                employee_order_id=new_employee_request_order.employee_order_id,
                inventory_id=inventory_id,
            )
            new_employee_request_order.employee_request_inventory_association.append(new_association)

        db.session.add(new_employee_request_order)
        db.session.commit()

        return jsonify(success={"message": "Employee request order successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@employee_request_api.get("/employee-request-order/all")
def get_all_employee_request_order():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = EmployeeRequestOrder.query.all()

        employee_request_order_data = []
        for data in query_data:
            employee_order = {
                "employee_order_id": data.employee_order_id,
                "employee_id": data.employee_id,
                "request_by": f"{data.employee.first_name} {data.employee.middle_name} "
                              f"{data.employee.last_name}",
                "request_order": [],
                "total_item_qty": data.total_item_qty,
                "order_date": data.order_date,
                "approved_by": data.approved_by,
                "approve_date": data.approved_date,
                "received_by": data.received_by,
                "received_date": data.received_date,
                "status": data.status
            }
            for order in data.employee_request_inventory_association:
                if order.inventory is not None:
                    employee_order["request_order"].append({
                        "employee_request_id": order.employee_request_id,
                        "inventory_id": order.inventory_id,
                        "item_name": order.inventory.item_name,
                        "item_qty": order.item_qty
                    })

            employee_request_order_data.append(employee_order)

        return jsonify(employee_request_order_data), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500



@employee_request_api.get("/employee-request-order/<int:employee_order_id>")
def get_specific_employee_order(employee_order_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = EmployeeRequestOrder.query.filter_by(employee_order_id=employee_order_id).first()

        if query_data is None:
            return jsonify(error={"message": "Employee request order id not found."}), 404

        employee_request_order_data = [{
            "employee_order_id": query_data.employee_order_id,
            "employee_id": query_data.employee_id,
            "request_by": f"{query_data.employee.first_name} {query_data.employee.middle_name} "
                          f"{query_data.employee.last_name}",
            "request_order": [{
                "employee_request_id": order.employee_request_id,
                "inventory_id": order.inventory_id,
                "item_name": order.inventory.item_name,
                "item_qty": order.item_qty
            } for order in query_data.employee_request_inventory_association],
            "total_item_qty": query_data.total_item_qty,
            "order_date": query_data.order_date,
            "approved_by": query_data.approved_by,
            "approve_date": query_data.approved_date,
            "received_by": query_data.received_by,
            "received_date": query_data.received_date,
            "status": query_data.status
        }]

        return jsonify(employee_request_order_data), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@employee_request_api.delete("/employee-request-order/delete/<int:employee_order_id>")
def delete_employee_order(employee_order_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        data = EmployeeRequestInventoryAssociation.query.filter_by(employee_order_id=employee_order_id).all()

        if data is None:
            return jsonify(error={"message": "Employee order id not found."}), 404

        for item in data:
            db.session.delete(item)

        data1 = EmployeeRequestOrder.query.filter_by(employee_order_id=employee_order_id).first()

        if data1 is None:
            return jsonify(error={"message": "Employee order id not found."}), 404

        db.session.delete(data1)
        db.session.commit()

        return jsonify(success={"message": "Employee request order successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@employee_request_api.post("/employee-request-order/approved/<int:employee_order_id>")
def approved_employee_order(employee_order_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        data = EmployeeRequestInventoryAssociation.query.filter_by(employee_order_id=employee_order_id).all()

        if not data:
            return jsonify(error={"message": "Employee order id not found."}), 404

        item_quantities = [int(qty.strip()) for qty in request.form.get("item_qty").split(',')]
        inventory_ids = [int(_id.strip()) for _id in request.form.get("inventory_id").split(',')]

        for qty, inventory_id in zip(item_quantities, inventory_ids):
            query_inventory = Inventory.query.filter_by(inventory_id=inventory_id).first()
            if query_inventory is None:
                return jsonify(error={"message": f"Inventory with id {inventory_id} not found."}), 404

            # Update EmployeeRequestInventoryAssociation item_qty
            for item in data:
                if item.inventory_id == inventory_id:
                    item.item_qty = qty

        # Update EmployeeRequestOrder status, approved_by, and approved_date
        data1 = EmployeeRequestOrder.query.filter_by(employee_order_id=employee_order_id).first()

        # Check if EmployeeRequestOrder object exists
        if data1 is None:
            return jsonify(error={"message": "Employee order id not found."}), 404

        data1.status = "Approved"
        data1.approved_by = request.form.get("approved_by")
        data1.approved_date = datetime.now()
        data1.total_item_qty = sum(item_quantities)

        db.session.commit()

        return jsonify(success={"message": "Employee order request successfully approved."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@employee_request_api.post("/employee-request-order/received/<int:employee_order_id>")
def received_employee_order(employee_order_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        data = EmployeeRequestInventoryAssociation.query.filter_by(employee_order_id=employee_order_id).all()

        if not data:
            return jsonify(error={"message": "Employee order id not found."}), 404

        for item in data:
            inventory_item = Inventory.query.get(item.inventory_id)

            if inventory_item:
                inventory_item.available_stock -= item.item_qty

                # Reevaluate item_status
                if int(inventory_item.available_stock) <= 0:
                    inventory_item.item_status = "Not Available"
                elif int(inventory_item.available_stock) <= int(inventory_item.reorder_level):
                    inventory_item.item_status = "Restock"
                else:
                    inventory_item.item_status = "Available"

        # Update EmployeeRequestOrder status, approved_by, and approved_date
        data1 = EmployeeRequestOrder.query.filter_by(employee_order_id=employee_order_id).first()

        # Check if EmployeeRequestOrder object exists
        if data1 is None:
            return jsonify(error={"message": "Employee order id not found."}), 404

        data1.received_by = request.form.get("received_by")
        data1.received_date = datetime.now()
        data1.status = "Received"

        db.session.commit()

        return jsonify(success={"message": "Employee order request successfully received and inventory updated."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500