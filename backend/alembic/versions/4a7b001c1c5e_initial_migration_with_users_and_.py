"""Initial migration with users and predictions tables

Revision ID: 4a7b001c1c5e
Revises:
Create Date: 2025-08-07 19:11:00.044484

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a7b001c1c5e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True, index=True),
        sa.Column("api_key_hash", sa.String(255), unique=True, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, default=sa.text("now()")),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("api_key_hash"),
    )

    # Create predictions table
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("team_name", sa.String(100), nullable=False, index=True),
        sa.Column("formation", sa.String(20), nullable=True),
        sa.Column("lineup", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, default=sa.text("now()"), index=True
        ),
        sa.Column("created_by", sa.String(100), nullable=True, index=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("predictions")
    op.drop_table("users")
