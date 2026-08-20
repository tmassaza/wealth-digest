"""Schema iniziale

Revision ID: 20250101_000001
Revises:
Create Date: 2025-01-01 00:00:01.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# Identificatori della revisione usati da Alembic.
revision = "20250101_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Attiva l'estensione vector prima di creare colonne vettoriali.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("profile_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_id"), "news", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_news_id"), table_name="news")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("news")
    op.drop_table("users")
