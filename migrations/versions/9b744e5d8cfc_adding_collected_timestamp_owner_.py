"""adding collected_timestamp, owner_collect, and owner_collect_timestamp fields to your ServiceTicket and SMS notify

Revision ID: 9b744e5d8cfc
Revises: ebe52ea8b39b
Create Date: 2024-02-06 22:32:17.082478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b744e5d8cfc'
down_revision = 'ebe52ea8b39b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_ticket', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sms_notification_completed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('sms_notification_10_days', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('sms_notification_30_days', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_ticket', schema=None) as batch_op:
        batch_op.drop_column('sms_notification_30_days')
        batch_op.drop_column('sms_notification_10_days')
        batch_op.drop_column('sms_notification_completed')

    # ### end Alembic commands ###
