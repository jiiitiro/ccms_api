"""empty message

Revision ID: 5d3cb21d8c8b
Revises: 5b09bb03d723
Create Date: 2024-04-12 23:24:00.765171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d3cb21d8c8b'
down_revision = '5b09bb03d723'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_order_inventory_association', schema=None) as batch_op:
        batch_op.add_column(sa.Column('inventory_association_id', sa.Integer(), autoincrement=True, nullable=False))
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_order_inventory_association', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('inventory_association_id')

    # ### end Alembic commands ###
