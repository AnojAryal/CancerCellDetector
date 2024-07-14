"""Upgrade detection_status to String(255)

Revision ID: b519ab7d3d77
Revises: f36dff5a2544
Create Date: 2024-07-14 09:44:14.654499

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b519ab7d3d77"
down_revision: Union[str, None] = "f36dff5a2544"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "lab_celltest",
        "detection_status",
        existing_type=sa.String(length=1),
        type_=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "lab_celltest",
        "detection_status",
        existing_type=sa.String(length=255),
        type_=sa.String(length=1),
        existing_nullable=False,
    )
