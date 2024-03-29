"""Add total_sales_amount column to PhoneListing

Revision ID: 93db02a883dc
Revises: c992cefab969
Create Date: 2024-01-21 23:20:09.184184

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93db02a883dc'
down_revision = 'c992cefab969'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('phone_listing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_sales_amount', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('phone_listing', schema=None) as batch_op:
        batch_op.drop_column('total_sales_amount')

    # ### end Alembic commands ###
