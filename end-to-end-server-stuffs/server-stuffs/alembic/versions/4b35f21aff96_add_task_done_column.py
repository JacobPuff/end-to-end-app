"""Add task done column

Revision ID: 4b35f21aff96
Revises: e1f57cad232d
Create Date: 2019-08-28 13:37:19.393155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b35f21aff96'
down_revision = 'e1f57cad232d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tasks', sa.Column('task_done', sa.Boolean, nullable=False))


def downgrade():
    op.drop_column('tasks', 'task_done')
