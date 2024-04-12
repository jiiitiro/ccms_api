"""change employeeid in booking nullable to false

Revision ID: 5298ecfdf1f7
Revises: 1376552bea5d
Create Date: 2024-04-09 14:50:32.709527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5298ecfdf1f7'
down_revision = '1376552bea5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.alter_column('employee_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.alter_column('employee_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###