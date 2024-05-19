"""empty message

Revision ID: 46d453d1bca5
Revises: b509d412c9df
Create Date: 2024-05-10 13:46:30.005687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46d453d1bca5'
down_revision = 'b509d412c9df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee_activity_logs_tbl',
    sa.Column('log_id', sa.Integer(), nullable=False),
    sa.Column('login_id', sa.Integer(), nullable=True),
    sa.Column('logs_description', sa.String(length=255), nullable=False),
    sa.Column('log_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['login_id'], ['employee_tbl.employee_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('employee_activity_logs_tbl')
    # ### end Alembic commands ###