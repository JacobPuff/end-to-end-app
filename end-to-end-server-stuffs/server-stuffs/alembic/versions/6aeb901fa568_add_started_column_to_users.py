"""Add started column to users

Revision ID: 6aeb901fa568
Revises: ca9c84325fe1
Create Date: 2019-11-26 14:05:19.593752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6aeb901fa568'
down_revision = 'ca9c84325fe1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('started', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=False))


def downgrade():
    op.drop_column('users', 'started')
