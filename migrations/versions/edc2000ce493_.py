"""empty message

Revision ID: edc2000ce493
Revises: 924adbb32b35
Create Date: 2024-04-23 15:16:56.614239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edc2000ce493'
down_revision = '924adbb32b35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('property_size_pricing_tbl',
    sa.Column('property_size_pricing_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('property_size', sa.String(length=255), nullable=False),
    sa.Column('pricing', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['service_tbl.service_id'], ),
    sa.PrimaryKeyConstraint('property_size_pricing_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('property_size_pricing_tbl')
    # ### end Alembic commands ###