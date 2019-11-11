"""start database

Revision ID: f3f26b38e6c4
Revises: aa221b3f04fe
Create Date: 2019-09-26 17:35:31.651437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3f26b38e6c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tasklists',
        sa.Column('list_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('list_name', sa.Text, nullable=False)
    )

    op.create_table(
        'tasks',
        sa.Column('task_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('list_id', sa.Integer, sa.ForeignKey('tasklists.list_id', ondelete='CASCADE')),
        sa.Column('task_name', sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table('tasks')
    op.drop_table('tasklists')
