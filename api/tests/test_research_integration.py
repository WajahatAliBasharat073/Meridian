"""End-to-end check of the research repository against the real
database: topic -> paper/note/experiment/milestone linkage, opportunity
CRUD, and per-user isolation.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import date

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models.core import User
from app.models.research import (
    ResearchExperiment,
    ResearchMilestone,
    ResearchNote,
    ResearchOpportunity,
    ResearchPaper,
    ResearchTopic,
)
from app.repositories import research as research_repo


@pytest.fixture
async def user() -> AsyncGenerator[tuple[AsyncSession, uuid.UUID], None]:
    session = SessionLocal()
    user_id = uuid.uuid4()
    session.add(User(id=user_id, email=f"research-test-{user_id}@test.local", settings={}))
    await session.commit()
    try:
        yield session, user_id
    finally:
        for model in (
            ResearchNote,
            ResearchExperiment,
            ResearchMilestone,
            ResearchPaper,
            ResearchOpportunity,
            ResearchTopic,
        ):
            await session.execute(delete(model).where(model.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        await session.close()
        await engine.dispose()


async def test_paper_note_and_experiment_link_back_to_their_topic(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    topic = await research_repo.create_topic(session, user_id, "LLM calibration", None)

    paper = await research_repo.create_paper(
        session, user_id, {"topic_id": topic.id, "title": "Calibrating LLMs", "status": "to_read"}
    )
    note = await research_repo.create_note(
        session, user_id, {"topic_id": topic.id, "paper_id": paper.id, "kind": "idea", "content": "Try X"}
    )
    experiment = await research_repo.create_experiment(
        session, user_id, {"topic_id": topic.id, "title": "Probe activations", "status": "planned"}
    )

    papers = await research_repo.list_papers(session, user_id, topic_id=topic.id)
    notes = await research_repo.list_notes(session, user_id, topic_id=topic.id)
    experiments = await research_repo.list_experiments(session, user_id, topic_id=topic.id)

    assert [p.id for p in papers] == [paper.id]
    assert [n.id for n in notes] == [note.id]
    assert [e.id for e in experiments] == [experiment.id]


async def test_papers_to_read_count_only_counts_that_status(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    await research_repo.create_paper(session, user_id, {"title": "A", "status": "to_read"})
    await research_repo.create_paper(session, user_id, {"title": "B", "status": "read"})
    await research_repo.create_paper(session, user_id, {"title": "C", "status": "to_read"})

    count = await research_repo.count_papers_to_read(session, user_id)
    assert count == 2


async def test_upcoming_milestones_excludes_completed_and_far_future(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    today = date(2026, 9, 15)
    await research_repo.create_milestone(
        session, user_id, {"title": "Soon", "target_date": date(2026, 9, 20), "status": "pending"}
    )
    await research_repo.create_milestone(
        session, user_id, {"title": "Far", "target_date": date(2027, 6, 1), "status": "pending"}
    )
    await research_repo.create_milestone(
        session, user_id, {"title": "Done", "target_date": date(2026, 9, 16), "status": "completed"}
    )

    upcoming = await research_repo.upcoming_milestones(session, user_id, today, within_days=30)
    assert [m.title for m in upcoming] == ["Soon"]


async def test_opportunity_status_transitions_and_add_to_goals_flow(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    opp = await research_repo.create_opportunity(
        session,
        user_id,
        {
            "venue_name": "NeurIPS 2027",
            "venue_type": "conference",
            "research_area": "LLM interpretability",
            "submission_deadline": date(2027, 5, 1),
            "relevance": "high",
        },
    )
    assert opp.status == "interested"

    updated = await research_repo.update_opportunity(session, user_id, opp.id, {"status": "shortlisted"})
    assert updated is not None
    assert updated.status == "shortlisted"


async def test_research_entities_are_isolated_per_user() -> None:
    session_a = SessionLocal()
    session_b = SessionLocal()
    user_a, user_b = uuid.uuid4(), uuid.uuid4()
    session_a.add_all(
        [
            User(id=user_a, email=f"research-a-{user_a}@test.local", settings={}),
            User(id=user_b, email=f"research-b-{user_b}@test.local", settings={}),
        ]
    )
    await session_a.commit()
    try:
        await research_repo.create_topic(session_a, user_a, "Only A's topic", None)
        await research_repo.create_topic(session_b, user_b, "Only B's topic", None)

        topics_a = await research_repo.list_topics(session_a, user_a)
        topics_b = await research_repo.list_topics(session_b, user_b)
        assert [t.title for t in topics_a] == ["Only A's topic"]
        assert [t.title for t in topics_b] == ["Only B's topic"]
    finally:
        await session_a.execute(delete(ResearchTopic).where(ResearchTopic.user_id.in_([user_a, user_b])))
        await session_a.execute(delete(User).where(User.id.in_([user_a, user_b])))
        await session_a.commit()
        await session_a.close()
        await session_b.close()
        await engine.dispose()
