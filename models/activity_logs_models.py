from db import db


class CustomerAdminActivityLogs(db.Model):
    __tablename__ = "customer_admin_activity_logs_tbl"
    log_id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('customer_admin_login_tbl.login_id'))
    logs_description = db.Column(db.String(255), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    customer_admin = db.relationship("CustomerAdminLogin", back_populates="customer_admin_activity_logs")


class BillingAdminActivityLogs(db.Model):
    __tablename__ = "booking_admin_activity_logs_tbl"
    log_id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('billing_admin_login_tbl.login_id'))
    logs_description = db.Column(db.String(255), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    billing_admin = db.relationship("BillingAdminLogin", back_populates="billing_admin_activity_logs")


class EmployeeAdminActivityLogs(db.Model):
    __tablename__ = "employee_admin_activity_logs_tbl"
    log_id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('employee_admin_login_tbl.login_id'))
    logs_description = db.Column(db.String(255), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    employee_admin = db.relationship("EmployeeAdminLogin", back_populates="employee_admin_activity_logs")


class InventoryAdminActivityLogs(db.Model):
    __tablename__ = "inventory_admin_activity_logs_tbl"
    log_id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('inventory_admin_login_tbl.login_id'))
    logs_description = db.Column(db.String(255), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    inventory_admin = db.relationship("InventoryAdminLogin", back_populates="inventory_admin_activity_logs")


class PayrollAdminActivityLogs(db.Model):
    __tablename__ = "payroll_admin_activity_logs_tbl"
    log_id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('payroll_admin_login_tbl.login_id'))
    logs_description = db.Column(db.String(255), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    payroll_admin = db.relationship("PayrollAdminLogin", back_populates="payroll_admin_activity_logs")


class SuperadminActivityLogs(db.Model):
    __tablename__ = "superadmin_activity_logs_tbl"
    log_id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('superadmin_login_tbl.login_id'))
    logs_description = db.Column(db.String(255), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    superadmin = db.relationship("SuperadminLogin", back_populates="superadmin_activity_logs")







