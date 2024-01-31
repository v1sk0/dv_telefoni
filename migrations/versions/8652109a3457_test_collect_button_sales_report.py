"""test collect button sales_report

Revision ID: 8652109a3457
Revises: 0fe5277853d3
Create Date: 2024-01-22 01:47:12.004121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8652109a3457'
down_revision = '0fe5277853d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('phone_listing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('state', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('phone_listing', schema=None) as batch_op:
        batch_op.drop_column('state')

    # ### end Alembic commands ###