"""add_case_interrogation_fields

Revision ID: a3946072bcfb
Revises: 
Create Date: 2026-02-21 21:42:51.436613

Adds 4 interrogation-context columns to the Case table so the
Interrogator agent has extracted_facts, prior_statements, exhibit_list,
and focus_areas available when generating deposition questions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a3946072bcfb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('Case', sa.Column('extractedFacts', sa.Text(), nullable=True))
    op.add_column('Case', sa.Column('priorStatements', sa.Text(), nullable=True))
    op.add_column('Case', sa.Column('exhibitList', sa.Text(), nullable=True))
    op.add_column('Case', sa.Column('focusAreas', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('Case', 'focusAreas')
    op.drop_column('Case', 'exhibitList')
    op.drop_column('Case', 'priorStatements')
    op.drop_column('Case', 'extractedFacts')
