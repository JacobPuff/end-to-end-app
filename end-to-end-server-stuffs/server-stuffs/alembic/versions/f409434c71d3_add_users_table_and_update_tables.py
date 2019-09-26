"""add users table and update tables

Revision ID: f409434c71d3
Revises: 
Create Date: 2019-08-06 14:43:20.178916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f409434c71d3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_name', sa.Text, nullable=False, unique=True),
        sa.Column('user_email', sa.String(254), nullable=False),
        sa.Column('user_pass', sa.Text, nullable=False)
    )
    op.drop_column('tasks', 'user_id')
    op.create_foreign_key(None, 'tasklists', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')


def downgrade():
    op.execute("TRUNCATE users CASCADE")
    op.drop_constraint('fk_tasklists_user_id_users', 'tasklists')
    op.drop_table('users')
    op.add_column('tasks', sa.Column('user_id', sa.Integer, nullable=False))
