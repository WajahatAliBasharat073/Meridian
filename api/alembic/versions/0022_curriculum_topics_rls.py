"""curriculum_topics rls

Revision ID: 0022_curriculum_topics_rls
Revises: 0021_learning_status
Create Date: 2026-09-10

curriculum_topics is reference data (phase/prerequisite graph, no user_id
column) exactly like problems/patterns/topic_guides — every other
reference table added since 0002_enable_rls got the standard read-only
policy for `authenticated` in the same migration that created it
(0014_dsa_topics_and_guides for topic_guides, for example). This one was
missed when 0019_curriculum_graph added the table alongside
learner_frontier (which did get its per-user policies). Closing the gap
for consistency — the API connects as the base postgres role and bypasses
RLS regardless (per 0002's docstring), so this has no effect on the app's
actual authorization, only on defence-in-depth for any other client.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0022_curriculum_topics_rls"
down_revision: str | None = "0021_learning_status"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE curriculum_topics ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY curriculum_topics_read_all ON curriculum_topics "
        "FOR SELECT TO authenticated USING (true)"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS curriculum_topics_read_all ON curriculum_topics")
    op.execute("ALTER TABLE curriculum_topics DISABLE ROW LEVEL SECURITY")
