"""Create SparePart, ServiceTicket, and ComputerListing models

Revision ID: ac6f281d7972
Revises: cc311c299bcb
Create Date: 2024-01-31 20:12:33.294866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac6f281d7972'
down_revision = 'cc311c299bcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_ticket', schema=None) as batch_op:
        batch_op.add_column(sa.Column('collected', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_ticket', schema=None) as batch_op:
        batch_op.drop_column('collected')

    # ### end Alembic commands ###