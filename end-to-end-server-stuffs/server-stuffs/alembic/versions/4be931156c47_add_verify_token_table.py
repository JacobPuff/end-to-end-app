"""add verify token table

Revision ID: 4be931156c47
Revises: 4b35f21aff96
Create Date: 2019-09-25 12:23:01.121259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4be931156c47'
down_revision = '4b35f21aff96'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'verifytokens',
        sa.Column('verifytoken_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id', ondelete='CASCADE')),
        sa.Column('started', sa.TIMESTAMP, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('token', sa.Text, nullable=False)
    )
    op.add_column('users', sa.Column('verified', sa.Boolean, default=False, server_default="f", nullable=False))



def downgrade():
    op.drop_table('verifytokens')
    op.drop_column('users', 'verified')
