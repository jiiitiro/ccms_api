"""empty message

Revision ID: 81f27ffc2486
Revises: 10ec45a091f1
Create Date: 2024-04-29 16:31:46.356683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81f27ffc2486'
down_revision = '10ec45a091f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.drop_column('additional_charge')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('additional_charge', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
