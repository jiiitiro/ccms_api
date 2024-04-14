import os
from flask import Blueprint, request, jsonify

from db import db
from models import Billing, Booking, Customer

billing_api = Blueprint("billing_api", __name__)

API_KEY = os.environ.get('API_KEY')


@billing_api.get("/billing/all")
def get_all_billing_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Billing.query.all()

        billing_data = []
        for data in query_data:

            billing_data.append({
                "invoice_id": data.invoice_id,
                "booking_id": data.booking_id,
                "customer_id": data.customer_id,
                "customer_name": f"{data.customer.first_name} {data.customer.middle_name} {data.customer.last_name}",
                "total_amount": data.total_amount,
                "method_of_payment": data.method_of_payment,
                "payment_status": data.payment_status,
                "service_status": data.service_status
            })

        return jsonify(success={"billing_data": billing_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@billing_api.get("/billing/<int:invoice_id>")
def get_specific_billing_data(invoice_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Billing.query.filter_by(invoice_id=invoice_id).first()

        if query_data is None:
            return jsonify(error={"message": "Invoice id not found."}), 404

        billing_data = [
            {
                "invoice_id": query_data.invoice_id,
                "booking_id": query_data.booking_id,
                "customer_id": query_data.customer_id,
                "customer_name": f"{query_data.customer.first_name} {query_data.customer.middle_name} "
                                 f"{query_data.customer.last_name}",
                "total_amount": query_data.total_amount,
                "payment_method": query_data.method_of_payment,
                "payment_status": query_data.payment_status,
                "service_status": query_data.service_status
            }
        ]

        return jsonify(success={"billing_data": billing_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@billing_api.post("/billing/add")
def add_billing_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_booking_id = Booking.query.filter_by(booking_id=request.form.get("booking_id")).first()

        if query_booking_id is None:
            return jsonify(error={"message": "Booking id not found."}), 404

        new_billing_data = Billing(
            booking_id=query_booking_id.booking_id,
            total_amount=query_booking_id.total_price,
            customer_id=query_booking_id.customer_id,
            method_of_payment="GCASH",
            payment_status="PAID",
        )

        # Update booking status to "PAID"
        query_booking_id.status = "PAID"

        # Commit changes to the database
        db.session.add(new_billing_data)
        db.session.commit()

        return jsonify(success={"message": "Billing successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@billing_api.delete("/billing/delete/<int:invoice_id>")
def delete_billing(invoice_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Billing.query.filter_by(invoice_id=invoice_id).first()

        if query_data is None:
            return jsonify(error={"message": "Billing id not found."}), 404

        db.session.delete(query_data)
        db.session.commit()

        return jsonify(success={"message": "Billing successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@billing_api.put("/billing/update/<int:invoice_id>")
def update_service_status(invoice_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Billing.query.get(invoice_id)

        if query_data is None:
            return jsonify(error={"message": "Invoice id not found."}), 404

        query_data.service_status = request.form.get("service_status")
        db.session.commit()

        return jsonify(success={"message": "Service status successfully updated."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500








