import os
from flask import Blueprint, request, jsonify
from db import db
from models import Billing, Booking


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

        billing_data = [
            {
                "invoice_id": data.invoice_id,
                "booking_id": data.booking_id,
                "total_amount": data.total_amount,
                "payment_status": data.payment_status,
            } for data in query_data
        ]

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
                "total_amount": query_data.total_amount,
                "payment_status": query_data.payment_status,
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

        new_booking_data = Booking(
            booking_id=request.form.get("booking_id"),
            total_amount=float(request.form.get("total_amount")),
            payment_status=request.form.get("payment_status")
        )

        db.session.add(new_booking_data)
        db.session.commit()

        return jsonify(success={"message": "Billing successfully added."}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500







