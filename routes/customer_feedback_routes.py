import os
from flask import Blueprint, request, jsonify
from db import db
from models import Customer, Billing, Service, CustomerFeedback


customerfeedback_api = Blueprint("customerfeedback_api", __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@customerfeedback_api.get("/customer-feedback/all")
def get_all_customer_feedback_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = CustomerFeedback.query.all()

        customer_feedback_data = [
            {
                "customer_feedback_id": data.customer_feedback_id,
                "invoice_id": data.invoice_id,
                "customer_id": data.billing.customer_id,
                "customer_name": f"{data.billing.customer.first_name} {data.billing.customer.middle_name} "
                                 f"{data.billing.customer.last_name}",
                "comment": data.comment,
                "rating": data.rating,
                "rating_status": data.rating_status,
                "service": data.billing.bookings.services.category,
            } for data in query_data
        ]

        return jsonify(success={"customer_feedback_data": customer_feedback_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@customerfeedback_api.get("/customer-feedback/<int:customer_feedback_id>")
def get_specific_customer_feedback_data(customer_feedback_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = CustomerFeedback.query.filter_by(customer_feedback_id=customer_feedback_id).first()

        if query_data is None:
            return jsonify(error={"message": "Customer feedback id not found."}), 404

        customer_feedback_data = [
            {
                "customer_feedback_id": query_data.customer_feedback_id,
                "invoice_id": query_data.invoice_id,
                "customer_id": query_data.billing.customer.customer_id,
                "customer_name": f"{query_data.billing.customer.first_name} {query_data.billing.customer.middle_name} "
                                 f"{query_data.billing.customer.last_name}",
                "comment": query_data.comment,
                "rating": query_data.rating,
                "rating_status": query_data.rating_status
            }
        ]

        return jsonify(success={"customer_feedback_data": customer_feedback_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@customerfeedback_api.post("/customer-feedback/add/<int:customer_id>")
def add_customer_feedback(customer_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_customer_id = Customer.query.filter_by(customer_id=customer_id).first()
        if query_customer_id is None:
            return jsonify(error={"message": "Customer id not found."}), 404

        query_invoice_id = Billing.query.filter_by(invoice_id=request.form.get("invoice_id")).first()
        if query_invoice_id is None:
            return jsonify(error={"message": "Invoice id not found."}), 404

        if query_invoice_id.bookings.service_status.lower() != "accomplished":
            return jsonify(error={"message": "Service must be accomplished first."}), 404

        new_customer_feedback = CustomerFeedback(
            invoice_id=request.form.get("invoice_id"),
            comment=request.form.get("comment"),
            rating=request.form.get("rating"),
            rating_status=CustomerFeedback.calculate_rating_status(int(request.form.get("rating"))),
        )

        db.session.add(new_customer_feedback)
        db.session.commit()

        return jsonify(success={"message": "Customer feedback successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@customerfeedback_api.delete("/customer-feedback/delete/<int:customer_feedback_id>")
def delete_feedback(customer_feedback_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = CustomerFeedback.query.filter_by(customer_feedback_id=customer_feedback_id).first()

        if query_data is None:
            return jsonify(error={"message": "Customer feedback id not found."}), 404

        db.session.delete(query_data)
        db.session.commit()

        return jsonify(success={"message": "Customer feedback successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


