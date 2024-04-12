from sqlalchemy.orm import relationship
from db import db


class Supplier(db.Model):
    __tablename__ = "supplier_tbl"
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    # Define relationship
    inventory = relationship("Inventory", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

    # Define relationship to PurchaseOrderInventoryAssociation
    purchase_order_associations = db.relationship("PurchaseOrderInventoryAssociation", back_populates="supplier")


class Inventory(db.Model):
    __tablename__ = 'inventory_tbl'
    inventory_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_tbl.supplier_id'), nullable=True)
    category = db.Column(db.String(255), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    available_stock = db.Column(db.Integer, nullable=False)
    used_item = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=True, default=0)
    item_status = db.Column(db.String(20), nullable=True)
    unit_price = db.Column(db.Float, nullable=True)

    # Define relationship to Supplier
    supplier = db.relationship("Supplier", back_populates="inventory")

    # Define relationship to PurchaseOrderInventoryAssociation
    purchase_order_associations = db.relationship("PurchaseOrderInventoryAssociation", back_populates="inventory")


class PurchaseOrderInventoryAssociation(db.Model):
    __tablename__ = "purchase_order_inventory_association_tbl"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_order_tbl.purchase_order_id"))
    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier_tbl.supplier_id"))
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory_tbl.inventory_id"))
    item_qty = db.Column(db.Integer, nullable=False)  # Move item_qty to this table

    # Define relationship to PurchaseOrder and Inventory
    purchase_order = db.relationship("PurchaseOrder", back_populates="purchase_order_associations")
    inventory = db.relationship("Inventory", back_populates="purchase_order_associations")
    supplier = db.relationship("Supplier", back_populates="purchase_order_associations")


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_order_tbl"
    purchase_order_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_tbl.supplier_id'), nullable=True)
    total_item_qty = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    prepared_by = db.Column(db.String(255), nullable=False)
    prepared_date = db.Column(db.Date, nullable=False)
    received_by = db.Column(db.String(255), nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)

    # Define relationship to Supplier
    supplier = db.relationship("Supplier", back_populates="purchase_orders")

    # Define relationship to PurchaseOrderInventoryAssociation
    purchase_order_associations = db.relationship("PurchaseOrderInventoryAssociation", back_populates="purchase_order")


class EmployeeRequestOrder(db.Model):
    __tablename__ = "employee_request_order_tbl"
    employee_order_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_tbl.employee_id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_tbl.inventory_id'), nullable=True)
    total_item_qty = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    approved_by = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')  # (e.g., Pending, Approved)
