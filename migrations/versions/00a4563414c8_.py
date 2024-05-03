"""empty message

Revision ID: 00a4563414c8
Revises: 30bdc4081014
Create Date: 2024-04-29 18:20:58.800917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00a4563414c8'
down_revision = '30bdc4081014'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('billing_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_date', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('reference_number', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('mobile_number', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('billing_tbl', schema=None) as batch_op:
        batch_op.drop_column('mobile_number')
        batch_op.drop_column('reference_number')
        batch_op.drop_column('payment_date')

    # ### end Alembic commands ###