from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from db import db


class Inventory(db.Model):
    __tablename__ = 'inventory_tbl'
    inventory_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    qty_in_hand = db.Column(db.Integer, nullable=False, default=0)
    qty_used = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=True)
    item_status = db.Column(db.String(20), nullable=True)

    @hybrid_property
    def available_stock(self):
        return self.qty_in_hand - self.qty_used


# Define event listener to enforce constraint and update item_status
@event.listens_for(Inventory, 'before_update')
def before_update_listener(mapper, connection, target):
    if target.qty_in_hand < target.qty_used:
        raise ValueError("Quantity in hand cannot be less than quantity used.")

    # Update item_status based on available_stock and reorder_level
    if target.available_stock > 0:
        target.item_status = "Available"
    elif target.available_stock == 0:
        target.item_status = "Not Available"
    elif target.available_stock <= target.reorder_level:
        target.item_status = "Restock"
