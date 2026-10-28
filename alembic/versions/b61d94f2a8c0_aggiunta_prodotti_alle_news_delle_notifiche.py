"""Salva i prodotti associati alle news delle notifiche.

Revision ID: b61d94f2a8c0
Revises: afe80abd0d0a
"""

from alembic import op
import sqlalchemy as sa


revision = "b61d94f2a8c0"
down_revision = "afe80abd0d0a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_news_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notification_news_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["notification_news_id"], ["notification_news.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notification_news_id", "product_id", name="uq_notification_news_products_pair"),
    )
    op.create_index("ix_notification_news_products_notification_news_id", "notification_news_products", ["notification_news_id"])
    op.create_index("ix_notification_news_products_product_id", "notification_news_products", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_news_products_product_id", table_name="notification_news_products")
    op.drop_index("ix_notification_news_products_notification_news_id", table_name="notification_news_products")
    op.drop_table("notification_news_products")
