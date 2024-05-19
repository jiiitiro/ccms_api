"""empty message

Revision ID: b509d412c9df
Revises: 4026f68e4c32
Create Date: 2024-05-10 13:08:24.403464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b509d412c9df'
down_revision = '4026f68e4c32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee_admin_login_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('consecutive_failed_login', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('failed_timer', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee_admin_login_tbl', schema=None) as batch_op:
        batch_op.drop_column('failed_timer')
        batch_op.drop_column('consecutive_failed_login')

    # ### end Alembic commands ###