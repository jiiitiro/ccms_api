"""empty message

Revision ID: 16db7e022b0e
Revises: 58ea1a786e40
Create Date: 2024-04-14 18:22:52.358907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16db7e022b0e'
down_revision = '58ea1a786e40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payroll_contribution_rate_tbl', schema=None) as batch_op:
        batch_op.add_column(sa.Column('minimum_rate', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payroll_contribution_rate_tbl', schema=None) as batch_op:
        batch_op.drop_column('minimum_rate')

    # ### end Alembic commands ###