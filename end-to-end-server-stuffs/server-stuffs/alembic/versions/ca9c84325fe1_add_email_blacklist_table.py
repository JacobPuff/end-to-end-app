"""add email blacklist table

Revision ID: ca9c84325fe1
Revises: f14319a23f42
Create Date: 2019-11-26 12:03:28.369786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca9c84325fe1'
down_revision = 'f14319a23f42'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'emailblacklist',
        sa.Column('email_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(254), nullable=False)
    )


def downgrade():
    op.drop_table('emailblacklist')
