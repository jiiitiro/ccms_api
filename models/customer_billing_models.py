from sqlalchemy import CheckConstraint
from db import db


class Customer(db.Model):
    __tablename__ = 'customer_tbl'
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    middle_name = db.Column(db.String(250), nullable=True)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_confirm = db.Column(db.Boolean, default=False)

    # Define relationship to the CustomerAddress class
    addresses = db.relationship('CustomerAddress', back_populates='customer', lazy=True)

    # Define relationship to the Booking class
    bookings = db.relationship('Booking', back_populates='customer', lazy=True)


class CustomerAddress(db.Model):
    __tablename__ = 'customer_address'
    address_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), nullable=False)
    houseno_street = db.Column(db.String(100), nullable=False)
    barangay = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)

    # Define relationship to the Customer class
    customer = db.relationship('Customer', back_populates='addresses')


# Define the Booking class
booking_service_addon_association = db.Table(
    'booking_service_addon_association',
    db.Column('booking_id', db.Integer, db.ForeignKey('booking_tbl.booking_id')),
    db.Column('service_addon_id', db.Integer, db.ForeignKey('service_addon_tbl.service_addon_id'))
)


class Booking(db.Model):
    __tablename__ = 'booking_tbl'
    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service_tbl.service_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'), nullable=True)
    booking_date = db.Column(db.DateTime, nullable=False)
    time_arrival = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(250), nullable=False)

    # Add a relationship to the Customer class
    customer = db.relationship('Customer', back_populates='bookings', lazy=True)
    services = db.relationship('Service', back_populates="bookings", lazy=True)
    service_addons = db.relationship(
        'ServiceAddon',
        secondary=booking_service_addon_association,
        backref=db.backref('bookings', lazy='dynamic')
    )


# Define the Service class
class Service(db.Model):
    __tablename__ = 'service_tbl'
    service_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

    bookings = db.relationship('Booking', back_populates='services', lazy=True)


class ServiceAddon(db.Model):
    __tablename__ = "service_addon_tbl"
    service_addon_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)


# Define the Billing class
class Billing(db.Model):
    __tablename__ = 'billing_tbl'
    invoice_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking_tbl.booking_id'), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(100), nullable=False)


# Define the CustomerFeedback class
class CustomerFeedback(db.Model):
    __tablename__ = "customer_feedback_tbl"
    customer_feedback_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('billing_tbl.invoice_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service_tbl.service_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    rating_status = db.Column(db.String(20), nullable=True)

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
    )

    @staticmethod
    def calculate_rating_status(rating):
        if rating == 1:
            return "Poor"
        elif rating == 2:
            return "Fair"
        elif rating == 3:
            return "Average"
        elif rating == 4:
            return "Good"
        elif rating == 5:
            return "Excellent"
        else:
            return "Invalid Rating"
