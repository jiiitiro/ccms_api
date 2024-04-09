import os
from flask import Blueprint, request, jsonify
from db import db
from models import Booking, Customer, Service, Employee, ServiceAddon
from datetime import datetime

booking_api = Blueprint("booking_api", __name__)

# api-key
API_KEY = os.environ.get('API_KEY')


@booking_api.get("/booking/all")
def get_all_billing_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Booking.query.all()

        booking_data = []
        for booking in query_data:
            booking_dict = {
                "booking_id": booking.booking_id,
                "customer_id": booking.customer_id,
                "employee_id": booking.employee_id,
                "booking_date": booking.booking_date,
                "time_arrival": booking.time_arrival,
                "status": booking.status
            }

            total_price = 0

            # Calculate total price of service
            service = Service.query.get(booking.service_id)
            if service:
                total_price += service.price

            # Include service addons if available
            if booking.service_addons:
                for addon in booking.service_addons:
                    total_price += addon.price

            booking_dict["total_price"] = total_price

            # Include service addons if available
            if booking.service_addons:
                booking_dict["service_addons"] = [
                    {
                        "service_addon_id": addon.service_addon_id,
                        "description": addon.description,
                        "price": addon.price
                    } for addon in booking.service_addons
                ]

            # Include service details
            service = Service.query.get(booking.service_id)
            if service:
                booking_dict["service"] = {
                    "service_id": service.service_id,
                    "category": service.category,
                    "description": service.description,
                    "price": service.price
                }

            booking_data.append(booking_dict)

        return jsonify(success={"booking_data": booking_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@booking_api.get("/booking/<int:booking_id>")
def get_specific_booking(booking_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Booking.query.filter_by(booking_id=booking_id).first()

        if query_data is None:
            return jsonify(error={"message": "Booking id not found."}), 404

        booking_data = [
            {
                "booking_id": query_data.booking_id,
                "customer_id": query_data.customer_id,
                "service_id": query_data.service_id,
                "employee_id": query_data.employee_id,
                "service_addon_id": query_data.service_addon_id,
                "booking_date": query_data.booking_date,
                "time_arrival": query_data.time_arrival,
                "status": query_data.status
            }
        ]

        return jsonify(success={"booking_data": booking_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@booking_api.post("/booking/add")
def add_booking():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_customer_id = Customer.query.filter_by(customer_id=request.form.get("customer_id")).first()
        if query_customer_id is None:
            return jsonify(error={"message": "Customer id not found."}), 404

        query_service_id = Service.query.filter_by(service_id=request.form.get("service_id")).first()
        if query_service_id is None:
            return jsonify(error={"message": "Service id not found."}), 404

        # Convert comma-separated string of service_addon_id values to a list of integers
        service_addon_ids = [int(id.strip()) for id in request.form.get("service_addon_id").split(',')]

        # Check if service_addon_ids is not empty
        if service_addon_ids:
            # Query the service addons with the specified IDs
            query_service_addon_ids = ServiceAddon.query.filter(
                ServiceAddon.service_addon_id.in_(service_addon_ids)).all()

            # Check if all service addons were found
            if len(query_service_addon_ids) != len(service_addon_ids):
                return jsonify(error={"message": "One or more service addon IDs not found."}), 404

            # Create a new booking
            new_booking = Booking(
                customer_id=query_customer_id.customer_id,
                service_id=query_service_id.service_id,
                booking_date=datetime.now(),
                time_arrival=request.form.get("time_arrival"),
                status="Processing"
            )

            # Add service addons to the booking
            new_booking.service_addons.extend(query_service_addon_ids)

        else:
            # Create a new booking
            new_booking = Booking(
                customer_id=query_customer_id.customer_id,
                service_id=query_service_id.service_id,
                booking_date=datetime.now(),
                time_arrival=request.form.get("time_arrival"),
                status="Processing"
            )

        # Commit changes to the database
        db.session.add(new_booking)
        db.session.commit()

        # Retrieve the service addon IDs associated with the new booking
        new_service_addon_ids = [addon.service_addon_id for addon in new_booking.service_addons]

        # Prepare response data
        new_booking_dict = {
            "booking_id": new_booking.booking_id,
            "customer_id": new_booking.customer_id,
            "service_id": new_booking.service_id,
            "employee_id": new_booking.employee_id,
            "service_addon_ids": new_service_addon_ids,  # Include service addon IDs in the response
            "booking_date": new_booking.booking_date,
            "time_arrival": new_booking.time_arrival,
            "status": new_booking.status
        }

        return (
            jsonify(success={"message": "New booking successfully added.", "new_booking_data": new_booking_dict}), 200)

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@booking_api.delete("/booking/delete/<int:booking_id>")
def delete_booking_data(booking_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = Booking.query.filter_by(booking_id=booking_id).first()

        if query_data is None:
            return jsonify(error={"message": "Booking id not found."}), 404

        db.session.delete(query_data)
        db.session.commit()

        return jsonify(success={"message": "Booking successfully deleted."}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500



