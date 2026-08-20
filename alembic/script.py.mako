"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Identificatori della revisione usati da Alembic.
# Questi placeholder vengono sostituiti automaticamente quando crei una migration.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    # Codice applicato quando esegui `alembic upgrade`.
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    # Codice di rollback quando esegui `alembic downgrade`.
    ${downgrades if downgrades else "pass"}
