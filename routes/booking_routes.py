import os
from flask import Blueprint, request, jsonify
from db import db
from models import Booking, Customer, Service, Employee, ServiceAddon, CustomerAddress, PropertySizePricing
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
                "customer_name": f"{booking.customer.first_name} {booking.customer.middle_name} "
                                 f"{booking.customer.last_name}",
                "customer_address_id": booking.address_id,
                "customer_address": f"{booking.address.houseno_street}, {booking.address.barangay}, "
                                    f"{booking.address.city}, {booking.address.region}, {booking.address.zipcode}",
                "customer_phone": booking.customer.phone,
                "booking_date": booking.booking_date,
                "time_arrival": booking.time_arrival,
                "booking_status": booking.booking_status,
                "property_size": booking.property_size_pricing.property_size,
                "total_price": booking.total_price,
                "notes": booking.notes,
                "service_status": booking.service_status
            }

            if booking.employee:
                booking_dict["assign_employee"] = [{
                    "employee_id": employee.employee_id,
                    "employee_name": f"{employee.first_name} {employee.middle_name} "
                                     f"{employee.last_name}"
                }for employee in booking.employee]

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

        booking = Booking.query.filter_by(booking_id=booking_id).first()

        if booking is None:
            return jsonify(error={"message": "Booking id not found."}), 404

        booking_data = []
        booking_dict = {
            "booking_id": booking.booking_id,
            "customer_id": booking.customer_id,
            "customer_name": f"{booking.customer.first_name} {booking.customer.middle_name} "
                             f"{booking.customer.last_name}",
            "customer_address": booking.address_id,
            "customer_phone": booking.customer.phone,
            "assign_employee": [],
            "booking_date": booking.booking_date,
            "time_arrival": booking.time_arrival,
            "booking_status": booking.booking_status,
            "property_size": booking.property_size_pricing.property_size,
            "total_price": booking.total_price,
            "notes": booking.notes,
            "service_status": booking.service_status
        }

        if booking.employee:
            booking_dict["assign_employee"] = [{
                "employee_id": employee.employee_id,
                "employee_name": f"{employee.first_name} {employee.middle_name} "
                                 f"{employee.last_name}"
            } for employee in booking.employee]

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


@booking_api.put("/booking/assign-employee/<int:booking_id>")
def assign_employee(booking_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_booking = Booking.query.filter_by(booking_id=booking_id).first()

        if query_booking is None:
            return jsonify(error={"message": "Booking id not found."}), 404

        employee_ids = [int(_id.strip()) for _id in request.form.get("employee_id").split(',')]

        query_employee = Employee.query.filter(Employee.employee_id.in_(employee_ids)).all()

        # Check if all service addons were found
        if len(query_employee) != len(employee_ids):
            return jsonify(error={"message": "One or more employee IDs not found."}), 404

        # Update the booking with the assigned employees
        query_booking.employee = query_employee
        query_booking.service = "Assigned"
        db.session.commit()

        return jsonify(success=True, message="Employees assigned successfully."), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@booking_api.post("/booking/add")
def add_booking():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_customer = Customer.query.filter_by(customer_id=request.form.get("customer_id")).first()

        if query_customer is None:
            return jsonify(error={"message": "Customer not found."}), 404

        query_service = Service.query.filter_by(service_id=request.form.get("service_id")).first()
        if query_service is None:
            return jsonify(error={"message": "Service not found."}), 404

        # Check if property_size_pricing_id is in query_service.property_size_pricing.property_size_pricing_id
        property_size_pricing_id = request.form.get("property_size_pricing_id")

        # Query property size pricing by ID
        property_size_pricing = PropertySizePricing.query.get(property_size_pricing_id)

        # Check if property size pricing is found
        if property_size_pricing is None or property_size_pricing not in query_service.property_size_pricing:
            return jsonify(error={"message": "Property size pricing ID not found in service."}), 404

        # Check if the address ID exists in the customer's addresses
        address_id = request.form.get("address_id")
        if address_id not in [str(addr.address_id) for addr in query_customer.addresses]:
            return jsonify(error={"message": "Customer address not found."}), 404

        # Convert comma-separated string of service_addon_id values to a list of integers
        service_addon_ids = [int(_id.strip()) for _id in request.form.get("service_addon_id").split(',')]

        # Query service addons with the specified IDs
        query_service_addons = ServiceAddon.query.filter(ServiceAddon.service_addon_id.in_(service_addon_ids)).all()

        # Check if all service addons were found
        if len(query_service_addons) != len(service_addon_ids):
            return jsonify(error={"message": "One or more service addon IDs not found."}), 404

        # Calculate total price
        total_price = (query_service.price + sum(addon.price for addon in query_service_addons) +
                       property_size_pricing.pricing)

        # Create a new booking
        new_booking = Booking(
            customer_id=query_customer.customer_id,
            service_id=query_service.service_id,
            property_size_pricing_id=property_size_pricing_id,
            address_id=request.form.get("address_id"),
            booking_date=datetime.now(),
            time_arrival=request.form.get("time_arrival"),
            booking_status="Processing",
            total_price=float(total_price),  # Assign total price to the booking
            notes=request.form.get("notes") if request.form.get("notes") is not None else None
        )

        # Add service addons to the booking
        new_booking.service_addons.extend(query_service_addons)

        # Commit changes to the database
        db.session.add(new_booking)
        db.session.commit()

        return jsonify(success={"message": "New booking successfully added."})

    except Exception as e:
        db.session.rollback()
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
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500




