"""add temp_email column to verifytokens table

Revision ID: f14319a23f42
Revises: aa221b3f04fe
Create Date: 2019-11-21 12:08:03.935646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f14319a23f42'
down_revision = 'aa221b3f04fe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('verifytokens', sa.Column('temp_email', sa.String(254), nullable=True, server_default=None))


def downgrade():
    op.drop_column('verifytokens', 'temp_email')
