"""empty message

Revision ID: 143a1af4f716
Revises: 1d05ec504351
Create Date: 2024-04-29 19:45:03.628488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '143a1af4f716'
down_revision = '1d05ec504351'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('billing_tbl', schema=None) as batch_op:
        batch_op.drop_column('service_status')

    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_status', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.drop_column('service_status')

    with op.batch_alter_table('billing_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_status', sa.VARCHAR(length=100), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
