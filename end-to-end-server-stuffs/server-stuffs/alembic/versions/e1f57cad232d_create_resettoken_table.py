"""create resettoken table

Revision ID: e1f57cad232d
Revises: 787d5421f927
Create Date: 2019-08-28 13:14:51.457023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f57cad232d'
down_revision = '787d5421f927'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'resettokens',
        sa.Column('resettoken_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id', ondelete='CASCADE')),
        sa.Column('started', sa.TIMESTAMP, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('token', sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table('resettokens')
