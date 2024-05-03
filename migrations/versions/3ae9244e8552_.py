"""empty message

Revision ID: 3ae9244e8552
Revises: 56f3a199f5f9
Create Date: 2024-04-27 21:08:18.810737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ae9244e8552'
down_revision = '56f3a199f5f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payroll_admin_activity_logs_tbl',
    sa.Column('log_id', sa.Integer(), nullable=False),
    sa.Column('login_id', sa.Integer(), nullable=True),
    sa.Column('logs_description', sa.String(length=255), nullable=False),
    sa.Column('log_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['login_id'], ['payroll_admin_login_tbl.login_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payroll_admin_activity_logs_tbl')
    # ### end Alembic commands ###