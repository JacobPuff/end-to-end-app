"""create sessions table and update ids

Revision ID: 787d5421f927
Revises: f409434c71d3
Create Date: 2019-08-08 16:36:20.162433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '787d5421f927'
down_revision = 'f409434c71d3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id', ondelete='CASCADE')),
        sa.Column('started', sa.TIMESTAMP, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('last_active', sa.TIMESTAMP, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('token', sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table('sessions')
