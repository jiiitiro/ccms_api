"""empty message

Revision ID: 9c8f45d5332f
Revises: 46d453d1bca5
Create Date: 2024-05-11 00:32:39.468561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c8f45d5332f'
down_revision = '46d453d1bca5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer_admin_login_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('consecutive_failed_login', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('failed_timer', sa.DateTime(), nullable=True))

    with op.batch_alter_table('inventory_admin_login_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('consecutive_failed_login', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('failed_timer', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventory_admin_login_tbl', schema=None) as batch_op:
        batch_op.drop_column('failed_timer')
        batch_op.drop_column('consecutive_failed_login')

    with op.batch_alter_table('customer_admin_login_tbl', schema=None) as batch_op:
        batch_op.drop_column('failed_timer')
        batch_op.drop_column('consecutive_failed_login')

    # ### end Alembic commands ###