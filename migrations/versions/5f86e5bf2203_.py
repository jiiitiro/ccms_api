"""empty message

Revision ID: 5f86e5bf2203
Revises: 4fea898a4955
Create Date: 2024-04-15 09:28:54.989256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f86e5bf2203'
down_revision = '4fea898a4955'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee_request_inventory_association_tbl',
    sa.Column('employee_request_id', sa.Integer(), nullable=False),
    sa.Column('employee_order_id', sa.Integer(), nullable=True),
    sa.Column('inventory_id', sa.Integer(), nullable=True),
    sa.Column('item_qty', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['employee_order_id'], ['employee_request_order_tbl.employee_order_id'], ),
    sa.ForeignKeyConstraint(['inventory_id'], ['inventory_tbl.inventory_id'], ),
    sa.PrimaryKeyConstraint('employee_request_id')
    )
    with op.batch_alter_table('employee_request_order_tbl', schema=None) as batch_op:
        batch_op.drop_constraint('employee_request_order_tbl_inventory_id_fkey', type_='foreignkey')
        batch_op.drop_column('inventory_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee_request_order_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('inventory_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('employee_request_order_tbl_inventory_id_fkey', 'inventory_tbl', ['inventory_id'], ['inventory_id'])

    op.drop_table('employee_request_inventory_association_tbl')
    # ### end Alembic commands ###