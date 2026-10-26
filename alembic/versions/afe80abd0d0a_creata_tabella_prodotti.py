"""creata tabella prodotti

Revision ID: afe80abd0d0a
Revises: c93100221884
Create Date: 2026-10-21 16:17:23.082472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificatori della revisione usati da Alembic.
# Questi placeholder vengono sostituiti automaticamente quando crei una migration.
revision = 'afe80abd0d0a'
down_revision = 'c93100221884'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("theme", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("characteristics", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(
        op.f("ix_products_id"),
        "products",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
