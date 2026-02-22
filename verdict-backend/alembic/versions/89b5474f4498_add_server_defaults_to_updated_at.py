"""add_server_defaults_to_updated_at

Revision ID: 89b5474f4498
Revises: a3946072bcfb
Create Date: 2026-02-21

Prisma managed updatedAt at the application layer, leaving no DB-level DEFAULT.
SQLAlchemy's server_default=func.now() requires a real DB default.
This migration adds DEFAULT NOW() to every updatedAt column so SQLAlchemy
INSERTs work without explicitly supplying the timestamp.
"""
from typing import Sequence, Union
from alembic import op

revision: str = '89b5474f4498'
down_revision: Union[str, None] = 'a3946072bcfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    'Alert',
    'AttorneyAnnotation',
    'Brief',
    'Case',
    'Document',
    'Firm',
    'Session',
    'User',
    'Witness',
]


def upgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE "{table}" ALTER COLUMN "updatedAt" SET DEFAULT NOW()')


def downgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE "{table}" ALTER COLUMN "updatedAt" DROP DEFAULT')
