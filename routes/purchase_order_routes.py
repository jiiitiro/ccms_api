import os
from flask import Blueprint, request, jsonify
from models import PurchaseOrder, EmployeeRequestOrder, Supplier, Inventory
from db import db
from datetime import datetime

from models.inventory_models import PurchaseOrderInventoryAssociation

purchase_order_api = Blueprint("purchase_order_api", __name__)


API_KEY = os.environ.get("API_KEY")


@purchase_order_api.get("/purchase-order/all")
def get_all_purchase_order_data():
    try:
        api_header_key = request.headers.get("x-api-key")
        if API_KEY != api_header_key:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = PurchaseOrder.query.all()

        purchase_order_data = []
        for data in query_data:
            purchase_order_item = {
                "purchase_order_id": data.purchase_order_id,
                "supplier_id": data.supplier_id,
                "inventory_items": [
                    {
                        "inventory_id": data.inventory_id,
                        "item_name": data.inventory.item_name,
                        "unit_price": data.inventory.unit_price,
                        "item_qty": data.item_qty
                    } for data in data.purchase_order_associations
                ],
                "total_item_qty": data.total_item_qty,
                "total_amount": data.total_amount,
                "status": data.status,
                "prepared_by": data.prepared_by,
                "prepared_date": data.prepared_date,
                "received_by": data.received_by,
                "received_date": data.received_date
            }
            purchase_order_data.append(purchase_order_item)

        return jsonify(success={"purchase_order_data": purchase_order_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)} "}), 500


@purchase_order_api.get("/purchase-order/<int:purchase_order_id>")
def get_purchase_order_data_by_id(purchase_order_id):
    try:
        api_header_key = request.headers.get("x-api-key")
        if API_KEY != api_header_key:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = PurchaseOrder.query.filter_by(purchase_order_id=purchase_order_id).first()

        if query_data is None:
            return jsonify(error={"message": "Purchase order id not found."}), 404

        purchase_order_data = [
            {
                "purchase_order_id": query_data.purchase_order_id,
                "supplier_id": query_data.supplier_id,
                "inventory_items": [
                    {
                        "inventory_id": data.inventory_id,
                        "item_name": data.inventory.item_name,
                        "unit_price": data.inventory.unit_price,
                        "item_qty": data.item_qty
                    } for data in query_data.purchase_order_associations
                ],
                "total_item_qty": query_data.total_item_qty,
                "total_amount": query_data.total_amount,
                "status": query_data.status,
                "prepared_by": query_data.prepared_by,
                "prepared_date": query_data.prepared_date,
                "received_by": query_data.received_by,
                "received_date": query_data.received_date
            }
        ]

        return jsonify(success={"purchase_order_data": purchase_order_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)} "}), 500


@purchase_order_api.post("/purchase-order/add")
def add_purchase_order():
    try:
        api_header_key = request.headers.get("x-api-key")
        if API_KEY != api_header_key:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        supplier_id = request.form.get("supplier_id")
        inventory_ids = [int(_id.strip()) for _id in request.form.get("inventory_id").split(',')]
        item_quantities = [int(qty.strip()) for qty in request.form.get("item_qty").split(',')]

        query_supplier = Supplier.query.filter_by(supplier_id=supplier_id).first()
        if query_supplier is None:
            return jsonify(error={"message": "Supplier id not found."}), 404

        if not query_supplier.inventory:
            return jsonify(error={"message": "No inventory items found for the supplier."}), 404

        # Check if all inventory_ids belong to the specified supplier
        query_inventories = Inventory.query.filter(
            Inventory.supplier_id == supplier_id,
            Inventory.inventory_id.in_(inventory_ids)
        ).all()

        if len(query_inventories) != len(inventory_ids):
            return jsonify(error={"message": "One or more inventory ids are not associated with the supplier."}), 404

        # Calculate the total price
        total_amount = sum(
            item_qty * inventory.unit_price for item_qty, inventory in zip(item_quantities, query_inventories))

        # Create a new purchase order
        new_purchase_order = PurchaseOrder(
            supplier_id=supplier_id,
            total_item_qty=sum(item_quantities),
            total_amount=total_amount,
            status="Pending",
            prepared_by=request.form.get("prepared_by"),
            prepared_date=datetime.now(),
        )

        # Create associations between purchase order and inventory items with their quantities
        for inventory_id, item_qty in zip(inventory_ids, item_quantities):
            new_association = PurchaseOrderInventoryAssociation(
                purchase_order_id=new_purchase_order.purchase_order_id,
                supplier_id=supplier_id,
                inventory_id=inventory_id,
                item_qty=item_qty
            )
            new_purchase_order.purchase_order_associations.append(new_association)

        db.session.add(new_purchase_order)
        db.session.commit()

        return jsonify(success={"message": "Purchase order successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)} "}), 500


async def create_pdf(purchase_order):
    purchase_order_data = {
        "purchase_order_id": purchase_order.purchase_order_id,
        "supplier_id": purchase_order.supplier_id,
        "supplier_name": purchase_order.supplier.supplier_name,

    }


@purchase_order_api.delete("/purchase-order/delete/<int:purchase_order_id>")
def delete_purchase_order(purchase_order_id):
    try:
        api_header_key = request.headers.get("x-api-key")
        if API_KEY != api_header_key:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data_po = PurchaseOrder.query.filter_by(purchase_order_id=purchase_order_id).first()

        if query_data_po is None:
            return jsonify(error={"message": "Purchase order id not found."}), 404

        # Fetch all associated PurchaseOrderInventoryAssociation objects
        query_data_po_associations = PurchaseOrderInventoryAssociation.query.filter_by(
            purchase_order_id=purchase_order_id).all()

        # Delete each associated object individually
        for association in query_data_po_associations:
            db.session.delete(association)

        # Delete the PurchaseOrder object
        db.session.delete(query_data_po)
        db.session.commit()

        return jsonify(success={"message": "Purchase order successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)} "}), 500


@purchase_order_api.post("/purchase-order/received/<purchase_order_id>")
def received_purchase_order(purchase_order_id):
    try:
        api_header_key = request.headers.get("x-api-key")
        if API_KEY != api_header_key:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = PurchaseOrder.query.filter_by(purchase_order_id=purchase_order_id).first()

        if query_data is None:
            return jsonify(error={"message": "Purchase order id not found."}), 404

        # Check if the purchase order is already received
        if query_data.status == 'Received':
            return jsonify(error={"message": "Purchase order has already been received."}), 400

        # Update the status of the purchase order to 'Received'
        query_data.status = 'Received'
        query_data.received_by = request.form.get('received_by')  # Assuming received_by is sent in the request JSON
        query_data.received_date = datetime.now()  # Set the received date to the current date and time

        # Update inventory quantities based on purchase order
        for association in query_data.purchase_order_associations:
            inventory_item = association.inventory

            # Update available stock in inventory
            inventory_item.available_stock += association.item_qty

            # Commit the changes to the inventory
            db.session.commit()

        # Commit changes to the purchase order
        db.session.commit()

        # Return success response
        return jsonify(success=True, message="Purchase order received successfully."), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)} "}), 500
