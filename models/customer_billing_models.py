from sqlalchemy import CheckConstraint
from db import db


class Customer(db.Model):
    __tablename__ = 'customer_tbl'
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    middle_name = db.Column(db.String(250), nullable=True)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(11), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    email_confirm = db.Column(db.Boolean, default=False)
    google_login = db.Column(db.Boolean)
    google_id = db.Column(db.String(200))

    # Define relationship
    addresses = db.relationship('CustomerAddress', back_populates='customer', lazy=True)
    bookings = db.relationship('Booking', back_populates='customer', lazy=True)
    billing = db.relationship("Billing", back_populates='customer', lazy=True)


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
    customer = db.relationship('Customer', back_populates='addresses', lazy=True)
    bookings = db.relationship("Booking", back_populates='address', lazy=True)


# Define the Booking class
booking_service_addon_association = db.Table(
    'booking_service_addon_association',
    db.Column('booking_id', db.Integer, db.ForeignKey('booking_tbl.booking_id')),
    db.Column('service_addon_id', db.Integer, db.ForeignKey('service_addon_tbl.service_addon_id'))
)

booking_employee_association = db.Table(
    'booking_employee_association',
    db.Column('booking_id', db.Integer, db.ForeignKey('booking_tbl.booking_id')),
    db.Column('employee_id', db.Integer, db.ForeignKey('employee_tbl.employee_id'))
)


class Booking(db.Model):
    __tablename__ = 'booking_tbl'
    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('customer_address.address_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service_tbl.service_id'), nullable=False)
    property_size_pricing_id = db.Column(db.Integer, db.ForeignKey('property_size_pricing_tbl.property_size_pricing_id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    time_arrival = db.Column(db.DateTime, nullable=False)
    booking_status = db.Column(db.String(250), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(250), nullable=True)
    service_status = db.Column(db.String(100), default="Not assigned")

    # Add a relationship
    customer = db.relationship('Customer', back_populates='bookings', lazy=True)
    services = db.relationship('Service', back_populates="bookings", lazy=True)
    billing = db.relationship('Billing', back_populates='bookings', lazy=True)
    address = db.relationship("CustomerAddress", back_populates='bookings', lazy=True)
    service_addons = db.relationship(
        'ServiceAddon',
        secondary=booking_service_addon_association,
        backref=db.backref('bookings', lazy='dynamic')
    )

    employee = db.relationship(
        'Employee',
        secondary=booking_employee_association,
        backref=db.backref('bookings', lazy='dynamic')
    )
    property_size_pricing = db.relationship('PropertySizePricing', back_populates='bookings', lazy=True)


# Define the Service class
class Service(db.Model):
    __tablename__ = 'service_tbl'
    service_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

    bookings = db.relationship('Booking', back_populates='services', lazy=True)
    property_size_pricing = db.relationship('PropertySizePricing', back_populates='services', lazy=True)


class PropertySizePricing(db.Model):
    __tablename__ = "property_size_pricing_tbl"
    property_size_pricing_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service_tbl.service_id'), nullable=True)
    property_size = db.Column(db.String(255), nullable=False)
    pricing = db.Column(db.Float, nullable=False)
    add_price_per_floor = db.Column(db.Float, nullable=True)

    services = db.relationship('Service', back_populates="property_size_pricing", lazy=True)
    bookings = db.relationship("Booking", back_populates='property_size_pricing', lazy=True)


class ServiceAddon(db.Model):
    __tablename__ = "service_addon_tbl"
    service_addon_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    pricing_description = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=False)


# Define the Billing class
class Billing(db.Model):
    __tablename__ = 'billing_tbl'
    invoice_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking_tbl.booking_id'), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_tbl.customer_id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    method_of_payment = db.Column(db.String(100), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    reference_number = db.Column(db.String(255), nullable=False)
    mobile_number = db.Column(db.String(11), nullable=False)
    payment_status = db.Column(db.String(100), nullable=False)

    # Add a relationship
    customer = db.relationship('Customer', back_populates='billing', lazy=True)
    bookings = db.relationship('Booking', back_populates='billing', lazy=True)
    feedback = db.relationship('CustomerFeedback', back_populates='billing', lazy=True)


# Define the CustomerFeedback class
class CustomerFeedback(db.Model):
    __tablename__ = "customer_feedback_tbl"
    customer_feedback_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('billing_tbl.invoice_id'), nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    rating_status = db.Column(db.String(20), nullable=True)

    billing = db.relationship('Billing', back_populates='feedback', lazy=True)

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
