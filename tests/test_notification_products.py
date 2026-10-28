"""Test PostgreSQL isolati, senza API LLM.

Eseguire dalla root con TEST_DATABASE_URL impostato a un PostgreSQL con pgvector:
    python -m unittest tests.test_notification_products -v

Ogni test crea uno schema temporaneo e lo rimuove tramite rollback, anche se
l'helper esegue commit. Le tabelle applicative non vengono modificate.
"""

import importlib.util
import os
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.notifications import get_user_last_notification, get_user_notifications
from app.db.base import Base
from app.db.models import News, Notification, NotificationNews, NotificationNewsProduct, Product, User
from app.helpers.notifications_helper import NotificationHelper
from app.services.generate_notification_service import (
    GeneratedNotificationNews, GeneratedProduct, GenerateNotificationService, UserGeneratedNotification,
)


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "Impostare TEST_DATABASE_URL per i test PostgreSQL")
class NotificationProductsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ["TEST_DATABASE_URL"])
        path = Path(__file__).resolve().parents[1] / "alembic/versions/b61d94f2a8c0_aggiunta_prodotti_alle_news_delle_notifiche.py"
        spec = importlib.util.spec_from_file_location("products_migration", path)
        cls.migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.migration)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.connection = self.engine.connect()
        self.addCleanup(self.connection.close)
        self.transaction = self.connection.begin()
        self.addCleanup(self.transaction.rollback)
        self.schema = "test_products_" + uuid.uuid4().hex
        self.connection.execute(sa.text(f"CREATE SCHEMA {self.schema}"))
        self.connection.execute(sa.text(f"SET LOCAL search_path TO {self.schema}, public"))
        old_tables = [table for table in Base.metadata.sorted_tables if table.name != "notification_news_products"]
        Base.metadata.create_all(self.connection, tables=old_tables, checkfirst=False)
        self.migrate("upgrade")
        self.db = Session(bind=self.connection, join_transaction_mode="create_savepoint")
        self.addCleanup(self.db.close)
        vector = [1.0] + [0.0] * 383
        self.user = User(name="Utente test", profile_text="Tecnologia", embedding=vector)
        self.news = [News(title=f"Chip {i}", content_text="Domanda di semiconduttori", summary="Chip",
                          embedding=vector, date=datetime.now(timezone.utc), link=f"https://example.invalid/{i}",
                          source="test", language="it") for i in range(2)]
        self.catalog = [Product(name=name, theme="Tecnologia", description="Test", characteristics="Test")
                        for name in ("ETF Chip", "ETF Tecnologia")]
        self.db.add_all([self.user, *self.news, *self.catalog])
        self.db.commit()
        self.user_id = self.user.id
        self.product_ids = [product.id for product in self.catalog]

    def migrate(self, direction):
        with Operations.context(MigrationContext.configure(self.connection)):
            getattr(self.migration, direction)()

    def generated_news(self, index, products):
        news = self.news[index]
        return GeneratedNotificationNews(
            id=str(news.id), title=news.title, date=str(news.date), summary="Sommario test",
            relevance="Motivo esteso", relevance_user="Motivo breve", source=news.source, link=news.link,
            products=[GeneratedProduct(id=self.product_ids[p], name="Nome LLM da correggere", reason=reason)
                      for p, reason in products],
        )

    def generate(self, news):
        generated = UserGeneratedNotification(generated_news=news)
        with patch.object(GenerateNotificationService, "run_openai", return_value=generated):
            return NotificationHelper().generate_notification(self.user, True, self.db)

    def test_products_survive_new_session_and_api_reads(self):
        generated = self.generate([
            self.generated_news(0, [(0, "Primo motivo"), (0, "Duplicato"), (1, "Secondo prodotto")]),
            self.generated_news(1, [(0, "Altro articolo, altro motivo")]),
        ])
        immediate = NotificationHelper().setup_notification_news_response_from_UserGeneratedNotification(generated, "28-10-2026")
        expected = {item["title"]: item["products"] for item in immediate["notification_news"]}
        self.assertEqual(len(expected[self.news[0].title]), 2)
        self.assertEqual(expected[self.news[0].title][0]["name"], "ETF Chip")
        self.db.close()
        with Session(bind=self.connection, join_transaction_mode="create_savepoint") as fresh:
            last = get_user_last_notification(self.user_id, fresh)
            archive = get_user_notifications(self.user_id, fresh)
            self.assertEqual({item["title"]: item["products"] for item in last["notification_news"]}, expected)
            self.assertEqual(archive[0], last)
            self.assertEqual(fresh.scalar(sa.select(sa.func.count()).select_from(NotificationNewsProduct)), 3)

    def test_no_products_and_historical_notifications(self):
        result = self.generate([self.generated_news(0, [])])
        immediate = NotificationHelper().setup_notification_news_response_from_UserGeneratedNotification(result, "28-10-2026")
        self.assertEqual(immediate["notification_news"][0]["products"], [])
        self.db.add(Notification(user_id=self.user_id, created_at=datetime.now(timezone.utc), notification_news=[
            NotificationNews(news_id=self.news[1].id, summary="Storico", relevance="Test", relevance_user="Test",
                             created_at=datetime.now(timezone.utc))]))
        self.db.commit()
        archive = get_user_notifications(self.user_id, self.db)
        self.assertTrue(all(item["products"] == [] for notification in archive for item in notification["notification_news"]))

    def test_empty_selection_creates_no_notification(self):
        result = self.generate([])
        self.assertEqual(result.generated_news, [])
        self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(Notification)), 0)
        self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(NotificationNewsProduct)), 0)

    def test_invalid_product_prevents_saving_notification(self):
        news = self.generated_news(0, [])
        news.products = [GeneratedProduct(id=99999, name="Inventato", reason="Motivo")]
        with self.assertRaises(HTTPException):
            self.generate([news])
        self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(Notification)), 0)

    def test_constraints_and_notification_delete_preserve_catalog(self):
        self.generate([self.generated_news(0, [(0, "Motivo")])])
        saved_news = self.db.scalars(sa.select(NotificationNews)).one()
        for product_id in (self.product_ids[0], 99999):
            with self.assertRaises(IntegrityError):
                with self.db.begin_nested():
                    self.db.add(NotificationNewsProduct(notification_news_id=saved_news.id, product_id=product_id, reason="Test"))
                    self.db.flush()
        self.db.delete(self.db.scalars(sa.select(Notification)).one())
        self.db.commit()
        self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(NotificationNewsProduct)), 0)
        self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(Product)), 2)

    def test_migration_downgrade_and_upgrade_preserve_existing_data(self):
        self.db.add(Notification(user_id=self.user_id, created_at=datetime.now(timezone.utc), notification_news=[
            NotificationNews(news_id=self.news[0].id, summary="Storico", relevance="Test", relevance_user="Test",
                             created_at=datetime.now(timezone.utc))]))
        self.db.commit()
        self.db.close()
        self.migrate("downgrade")
        self.assertNotIn("notification_news_products", sa.inspect(self.connection).get_table_names(schema=self.schema))
        self.assertEqual(self.connection.scalar(sa.text("SELECT count(*) FROM users")), 1)
        self.assertEqual(self.connection.scalar(sa.text("SELECT count(*) FROM products")), 2)
        self.migrate("upgrade")
        self.assertIn("notification_news_products", sa.inspect(self.connection).get_table_names(schema=self.schema))
        self.assertEqual(self.connection.scalar(sa.text("SELECT count(*) FROM notifications")), 1)
        self.assertEqual(self.connection.scalar(sa.text("SELECT count(*) FROM notification_news")), 1)
        self.assertEqual(self.connection.scalar(sa.text("SELECT count(*) FROM notification_news_products")), 0)

    def test_failed_product_insert_rolls_back_entire_notification(self):
        self.db.close()
        self.connection.execute(sa.text(
            "ALTER TABLE notification_news_products ADD CONSTRAINT test_insert_failure "
            "CHECK (reason <> 'Errore simulato')"
        ))
        self.user = self.db.get(User, self.user_id)
        self.news = self.db.scalars(sa.select(News).order_by(News.id)).all()
        with self.assertRaises(IntegrityError):
            self.generate([self.generated_news(0, [(0, "Errore simulato")])])
        self.db.rollback()
        for model in (Notification, NotificationNews, NotificationNewsProduct):
            self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(model)), 0)
        self.assertEqual(self.db.scalar(sa.select(sa.func.count()).select_from(Product)), 2)


if __name__ == "__main__":
    unittest.main()
