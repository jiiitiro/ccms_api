"""empty message

Revision ID: 0dad45b94c90
Revises: a1e1261f6457
Create Date: 2024-04-13 01:28:50.082207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dad45b94c90'
down_revision = 'a1e1261f6457'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_order_inventory_association', schema=None) as batch_op:
        batch_op.add_column(sa.Column('supplier_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'supplier_tbl', ['supplier_id'], ['supplier_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_order_inventory_association', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('supplier_id')

    # ### end Alembic commands ###