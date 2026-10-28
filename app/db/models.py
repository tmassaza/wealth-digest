from __future__ import annotations

from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """Profilo utente usato per il matching con le notizie."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_interval_days: Mapped[int] = mapped_column(default=1)
    profile_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class News(Base):
    """Notizia con testo ed embedding associato."""

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    link: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String(500), nullable=False)
    language: Mapped[str] = mapped_column(String(500), nullable=False)
    newsdata_id: Mapped[str] = mapped_column(Text, nullable=True)

class Notification(Base):
    """Notifiche generate per ogni utente"""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    notification_news: Mapped[list["NotificationNews"]] = relationship(
        back_populates="notification",
        cascade="all, delete-orphan",
    )

class NotificationNews(Base):
    """News utilizzate in ogni notifica"""

    __tablename__ = "notification_news"

    id: Mapped[int] = mapped_column(primary_key=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id"), nullable=False, index=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    relevance: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_user: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    notification: Mapped["Notification"] = relationship(back_populates="notification_news")
    news: Mapped["News"] = relationship()
    products: Mapped[list["NotificationNewsProduct"]] = relationship(
        back_populates="notification_news",
        cascade="all, delete-orphan",
        order_by="NotificationNewsProduct.id",
    )


class NotificationNewsProduct(Base):
    """Prodotto associato a una news di una notifica, con motivazione specifica."""

    __tablename__ = "notification_news_products"
    __table_args__ = (
        UniqueConstraint("notification_news_id", "product_id", name="uq_notification_news_products_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    notification_news_id: Mapped[int] = mapped_column(
        ForeignKey("notification_news.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    notification_news: Mapped["NotificationNews"] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship()

class Product(Base):
    """Prodotto disponibile per il matching con gli articoli."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    characteristics: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
