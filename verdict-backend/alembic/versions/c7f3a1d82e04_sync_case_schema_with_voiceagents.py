"""sync_case_schema_with_voiceagents

Revision ID: c7f3a1d82e04
Revises: 89b5474f4498
Create Date: 2026-02-22

Renames the legacy Prisma-generated columns on the Case table and adds the
three new columns required by the voiceagents VerdictCase schema so that the
ElevenLabs Conversational AI WebSocket logic can be served directly from the
main PostgreSQL database without any field mapping shims.

Changes
-------
  RENAME  "name"          -> "caseName"
  RENAME  "opposingFirm"  -> "opposingParty"
  ADD     "witnessName"   VARCHAR (nullable)
  ADD     "witnessRole"   VARCHAR (nullable)
  ADD     "aggressionLevel" VARCHAR (nullable)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c7f3a1d82e04"
down_revision: Union[str, None] = "89b5474f4498"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename "name" -> "caseName"
    op.alter_column("Case", "name", new_column_name="caseName")

    # Rename "opposingFirm" -> "opposingParty"
    op.alter_column("Case", "opposingFirm", new_column_name="opposingParty")

    # Add the three new denormalised witness / aggression columns
    op.add_column("Case", sa.Column("witnessName", sa.String(), nullable=True))
    op.add_column("Case", sa.Column("witnessRole", sa.String(), nullable=True))
    op.add_column("Case", sa.Column("aggressionLevel", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("Case", "aggressionLevel")
    op.drop_column("Case", "witnessRole")
    op.drop_column("Case", "witnessName")

    op.alter_column("Case", "opposingParty", new_column_name="opposingFirm")
    op.alter_column("Case", "caseName", new_column_name="name")
