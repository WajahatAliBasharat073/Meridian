"""separate the topic gate's "must be able to do" list from its reading list

Revision ID: 0016_gate_requirements
Revises: 0015_topic_verification
Create Date: 2026-09-08

The gate's checklist was being generated from `topic_guides.types` +
`operations`, which are *reading* material — the landscape of a topic,
including things worth knowing about but never implementing. Reusing them as
a build checklist produced nonsense: Arrays demanded twelve items including
"Static array" and "Dynamic array" (Python hands you both), plus "Binary
search" and "Sort", which belong to the Binary Search topic's own gate.

Twelve items at an 80% coverage bar is ten required demonstrations, most of
them not demonstrable — which pushes straight to the override, and an
override teaches nothing. So the gate gets its own short, hand-picked list
of things that genuinely can be written or shown, and the guide keeps its
reading list unchanged.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0016_gate_requirements"
down_revision: str | None = "0015_topic_verification"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "topic_guides",
        sa.Column(
            "gate_requirements",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )


def downgrade() -> None:
    op.drop_column("topic_guides", "gate_requirements")
