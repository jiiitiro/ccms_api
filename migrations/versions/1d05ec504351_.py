"""empty message

Revision ID: 1d05ec504351
Revises: 00a4563414c8
Create Date: 2024-04-29 19:01:54.089797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d05ec504351'
down_revision = '00a4563414c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('property_size_pricing_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'property_size_pricing_tbl', ['property_size_pricing_id'], ['property_size_pricing_id'])
        batch_op.drop_column('property_size')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('property_size', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('property_size_pricing_id')

    # ### end Alembic commands ###
