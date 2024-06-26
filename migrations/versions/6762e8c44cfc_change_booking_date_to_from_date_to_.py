"""change booking_date to from Date to DateTime in booking_tbl

Revision ID: 6762e8c44cfc
Revises: 1da0aa55788a
Create Date: 2024-04-09 17:12:06.569370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6762e8c44cfc'
down_revision = '1da0aa55788a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.alter_column('booking_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking_tbl', schema=None) as batch_op:
        batch_op.alter_column('booking_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False)

    # ### end Alembic commands ###
