"""Delete all data from users table

Revision ID: f36dff5a2544
Revises: 7aa1ca73a12a
Create Date: 2024-05-20 13:52:37.290678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f36dff5a2544'
down_revision: Union[str, None] = '7aa1ca73a12a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("DELETE FROM users")

def downgrade():
    op.execute("INSERT INTO users SELECT * FROM users_backup")