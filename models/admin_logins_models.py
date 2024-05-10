from flask_login import UserMixin
from db import db


# Define the payroll_login_tbl
class BillingAdminLogin(db.Model):
    __tablename__ = "billing_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)
    consecutive_failed_login = db.Column(db.Integer, nullable=True)
    failed_timer = db.Column(db.DateTime, nullable=True)

    billing_admin_activity_logs = db.relationship("BillingAdminActivityLogs", back_populates="billing_admin")


class PayrollAdminLogin(db.Model):
    __tablename__ = "payroll_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)
    consecutive_failed_login = db.Column(db.Integer, nullable=True)
    failed_timer = db.Column(db.DateTime, nullable=True)

    payroll_admin_activity_logs = db.relationship("PayrollAdminActivityLogs", back_populates="payroll_admin")


class EmployeeAdminLogin(db.Model):
    __tablename__ = "employee_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)
    consecutive_failed_login = db.Column(db.Integer, nullable=True)
    failed_timer = db.Column(db.DateTime, nullable=True)

    employee_admin_activity_logs = db.relationship("EmployeeAdminActivityLogs", back_populates="employee_admin")


class CustomerAdminLogin(db.Model):
    __tablename__ = "customer_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)

    customer_admin_activity_logs = db.relationship("CustomerAdminActivityLogs", back_populates="customer_admin")


class InventoryAdminLogin(db.Model):
    __tablename__ = "inventory_admin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)

    inventory_admin_activity_logs = db.relationship("InventoryAdminActivityLogs", back_populates="inventory_admin")


class SuperadminLogin(UserMixin, db.Model):
    __tablename__ = "superadmin_login_tbl"
    login_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    email_confirm = db.Column(db.Boolean, default=False)
    consecutive_failed_login = db.Column(db.Integer, nullable=True)
    failed_timer = db.Column(db.DateTime, nullable=True)

    superadmin_activity_logs = db.relationship("SuperadminActivityLogs", back_populates="superadmin")

    # Implement the get_id() method to return the user's id
    def get_id(self):
        return str(self.login_id)
