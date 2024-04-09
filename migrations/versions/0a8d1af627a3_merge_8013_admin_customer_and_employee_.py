"""merge 8013, admin, customer and employee data

Revision ID: 0a8d1af627a3
Revises: 8013dd773e26, admin_login_data, customer_data, employee_data
Create Date: 2024-04-09 11:56:32.402061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a8d1af627a3'
down_revision = ('8013dd773e26', 'admin_login_data', 'customer_data', 'employee_data')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
