"""test not collected to all phones

Revision ID: ac590c126d40
Revises: c85e36952b0c
Create Date: 2024-01-22 03:01:28.087750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac590c126d40'
down_revision = 'c85e36952b0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('phone_listing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('collected', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('phone_listing', schema=None) as batch_op:
        batch_op.drop_column('collected')

    # ### end Alembic commands ###
