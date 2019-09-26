"""Make user_email unique

Revision ID: aa221b3f04fe
Revises: 4be931156c47
Create Date: 2019-09-26 12:35:44.144945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa221b3f04fe'
down_revision = '4be931156c47'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "users", ["user_email"])


def downgrade():
    op.drop_constraint("uq_users_user_email", "users")
