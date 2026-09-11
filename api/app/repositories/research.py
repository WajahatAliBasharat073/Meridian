"""CRUD for the six research command-center tables. Plain reference-data
CRUD, same shape throughout: list/create/update/delete, ownership checked
on every read past the list endpoint."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.research import (
    ResearchExperiment,
    ResearchMilestone,
    ResearchNote,
    ResearchOpportunity,
    ResearchPaper,
    ResearchTopic,
)

# ----------------------------------------------------------------- topics


async def list_topics(session: AsyncSession, user_id: uuid.UUID) -> list[ResearchTopic]:
    result = await session.execute(
        select(ResearchTopic).where(ResearchTopic.user_id == user_id).order_by(ResearchTopic.id.desc())
    )
    return list(result.scalars().all())


async def get_topic(session: AsyncSession, user_id: uuid.UUID, topic_id: int) -> ResearchTopic | None:
    topic = await session.get(ResearchTopic, topic_id)
    return topic if topic is not None and topic.user_id == user_id else None


async def create_topic(
    session: AsyncSession, user_id: uuid.UUID, title: str, description: str | None
) -> ResearchTopic:
    topic = ResearchTopic(user_id=user_id, title=title, description=description)
    session.add(topic)
    await session.commit()
    await session.refresh(topic)
    return topic


async def update_topic(
    session: AsyncSession, user_id: uuid.UUID, topic_id: int, fields: dict[str, object]
) -> ResearchTopic | None:
    topic = await get_topic(session, user_id, topic_id)
    if topic is None:
        return None
    for key, value in fields.items():
        setattr(topic, key, value)
    await session.commit()
    await session.refresh(topic)
    return topic


async def delete_topic(session: AsyncSession, user_id: uuid.UUID, topic_id: int) -> bool:
    topic = await get_topic(session, user_id, topic_id)
    if topic is None:
        return False
    await session.delete(topic)
    await session.commit()
    return True


# ----------------------------------------------------------------- papers


async def list_papers(
    session: AsyncSession, user_id: uuid.UUID, topic_id: int | None = None, status_filter: str | None = None
) -> list[ResearchPaper]:
    query = select(ResearchPaper).where(ResearchPaper.user_id == user_id)
    if topic_id is not None:
        query = query.where(ResearchPaper.topic_id == topic_id)
    if status_filter:
        query = query.where(ResearchPaper.status == status_filter)
    result = await session.execute(query.order_by(ResearchPaper.id.desc()))
    return list(result.scalars().all())


async def get_paper(session: AsyncSession, user_id: uuid.UUID, paper_id: int) -> ResearchPaper | None:
    paper = await session.get(ResearchPaper, paper_id)
    return paper if paper is not None and paper.user_id == user_id else None


async def create_paper(session: AsyncSession, user_id: uuid.UUID, fields: dict[str, object]) -> ResearchPaper:
    paper = ResearchPaper(user_id=user_id, **fields)
    session.add(paper)
    await session.commit()
    await session.refresh(paper)
    return paper


async def update_paper(
    session: AsyncSession, user_id: uuid.UUID, paper_id: int, fields: dict[str, object]
) -> ResearchPaper | None:
    paper = await get_paper(session, user_id, paper_id)
    if paper is None:
        return None
    for key, value in fields.items():
        setattr(paper, key, value)
    await session.commit()
    await session.refresh(paper)
    return paper


async def delete_paper(session: AsyncSession, user_id: uuid.UUID, paper_id: int) -> bool:
    paper = await get_paper(session, user_id, paper_id)
    if paper is None:
        return False
    await session.delete(paper)
    await session.commit()
    return True


# ------------------------------------------------------------------ notes


async def list_notes(
    session: AsyncSession,
    user_id: uuid.UUID,
    topic_id: int | None = None,
    paper_id: int | None = None,
    kind: str | None = None,
) -> list[ResearchNote]:
    query = select(ResearchNote).where(ResearchNote.user_id == user_id)
    if topic_id is not None:
        query = query.where(ResearchNote.topic_id == topic_id)
    if paper_id is not None:
        query = query.where(ResearchNote.paper_id == paper_id)
    if kind:
        query = query.where(ResearchNote.kind == kind)
    result = await session.execute(query.order_by(ResearchNote.id.desc()))
    return list(result.scalars().all())


async def create_note(session: AsyncSession, user_id: uuid.UUID, fields: dict[str, object]) -> ResearchNote:
    note = ResearchNote(user_id=user_id, **fields)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def delete_note(session: AsyncSession, user_id: uuid.UUID, note_id: int) -> bool:
    note = await session.get(ResearchNote, note_id)
    if note is None or note.user_id != user_id:
        return False
    await session.delete(note)
    await session.commit()
    return True


# ------------------------------------------------------------ experiments


async def list_experiments(
    session: AsyncSession, user_id: uuid.UUID, topic_id: int | None = None
) -> list[ResearchExperiment]:
    query = select(ResearchExperiment).where(ResearchExperiment.user_id == user_id)
    if topic_id is not None:
        query = query.where(ResearchExperiment.topic_id == topic_id)
    result = await session.execute(query.order_by(ResearchExperiment.id.desc()))
    return list(result.scalars().all())


async def get_experiment(
    session: AsyncSession, user_id: uuid.UUID, experiment_id: int
) -> ResearchExperiment | None:
    experiment = await session.get(ResearchExperiment, experiment_id)
    return experiment if experiment is not None and experiment.user_id == user_id else None


async def create_experiment(
    session: AsyncSession, user_id: uuid.UUID, fields: dict[str, object]
) -> ResearchExperiment:
    experiment = ResearchExperiment(user_id=user_id, **fields)
    session.add(experiment)
    await session.commit()
    await session.refresh(experiment)
    return experiment


async def update_experiment(
    session: AsyncSession, user_id: uuid.UUID, experiment_id: int, fields: dict[str, object]
) -> ResearchExperiment | None:
    experiment = await get_experiment(session, user_id, experiment_id)
    if experiment is None:
        return None
    for key, value in fields.items():
        setattr(experiment, key, value)
    await session.commit()
    await session.refresh(experiment)
    return experiment


async def delete_experiment(session: AsyncSession, user_id: uuid.UUID, experiment_id: int) -> bool:
    experiment = await get_experiment(session, user_id, experiment_id)
    if experiment is None:
        return False
    await session.delete(experiment)
    await session.commit()
    return True


# ------------------------------------------------------------- milestones


async def list_milestones(
    session: AsyncSession, user_id: uuid.UUID, topic_id: int | None = None
) -> list[ResearchMilestone]:
    query = select(ResearchMilestone).where(ResearchMilestone.user_id == user_id)
    if topic_id is not None:
        query = query.where(ResearchMilestone.topic_id == topic_id)
    result = await session.execute(query.order_by(ResearchMilestone.target_date.asc().nulls_last()))
    return list(result.scalars().all())


async def get_milestone(
    session: AsyncSession, user_id: uuid.UUID, milestone_id: int
) -> ResearchMilestone | None:
    milestone = await session.get(ResearchMilestone, milestone_id)
    return milestone if milestone is not None and milestone.user_id == user_id else None


async def create_milestone(
    session: AsyncSession, user_id: uuid.UUID, fields: dict[str, object]
) -> ResearchMilestone:
    milestone = ResearchMilestone(user_id=user_id, **fields)
    session.add(milestone)
    await session.commit()
    await session.refresh(milestone)
    return milestone


async def update_milestone(
    session: AsyncSession, user_id: uuid.UUID, milestone_id: int, fields: dict[str, object]
) -> ResearchMilestone | None:
    milestone = await get_milestone(session, user_id, milestone_id)
    if milestone is None:
        return None
    for key, value in fields.items():
        setattr(milestone, key, value)
    await session.commit()
    await session.refresh(milestone)
    return milestone


async def delete_milestone(session: AsyncSession, user_id: uuid.UUID, milestone_id: int) -> bool:
    milestone = await get_milestone(session, user_id, milestone_id)
    if milestone is None:
        return False
    await session.delete(milestone)
    await session.commit()
    return True


# ---------------------------------------------------------- opportunities


async def list_opportunities(
    session: AsyncSession, user_id: uuid.UUID, status_filter: str | None = None
) -> list[ResearchOpportunity]:
    query = select(ResearchOpportunity).where(ResearchOpportunity.user_id == user_id)
    if status_filter:
        query = query.where(ResearchOpportunity.status == status_filter)
    result = await session.execute(query.order_by(ResearchOpportunity.submission_deadline.asc().nulls_last()))
    return list(result.scalars().all())


async def get_opportunity(
    session: AsyncSession, user_id: uuid.UUID, opportunity_id: int
) -> ResearchOpportunity | None:
    opp = await session.get(ResearchOpportunity, opportunity_id)
    return opp if opp is not None and opp.user_id == user_id else None


async def create_opportunity(
    session: AsyncSession, user_id: uuid.UUID, fields: dict[str, object]
) -> ResearchOpportunity:
    opp = ResearchOpportunity(user_id=user_id, **fields)
    session.add(opp)
    await session.commit()
    await session.refresh(opp)
    return opp


async def update_opportunity(
    session: AsyncSession, user_id: uuid.UUID, opportunity_id: int, fields: dict[str, object]
) -> ResearchOpportunity | None:
    opp = await get_opportunity(session, user_id, opportunity_id)
    if opp is None:
        return None
    for key, value in fields.items():
        setattr(opp, key, value)
    await session.commit()
    await session.refresh(opp)
    return opp


async def delete_opportunity(session: AsyncSession, user_id: uuid.UUID, opportunity_id: int) -> bool:
    opp = await get_opportunity(session, user_id, opportunity_id)
    if opp is None:
        return False
    await session.delete(opp)
    await session.commit()
    return True


# --------------------------------------------------------- at-a-glance


async def count_papers_to_read(session: AsyncSession, user_id: uuid.UUID) -> int:
    result = await session.execute(
        select(ResearchPaper).where(ResearchPaper.user_id == user_id, ResearchPaper.status == "to_read")
    )
    return len(result.scalars().all())


async def upcoming_milestones(
    session: AsyncSession, user_id: uuid.UUID, today: date, within_days: int = 30
) -> list[ResearchMilestone]:

    result = await session.execute(
        select(ResearchMilestone)
        .where(
            ResearchMilestone.user_id == user_id,
            ResearchMilestone.status.in_(("pending", "in_progress")),
            ResearchMilestone.target_date.is_not(None),
            ResearchMilestone.target_date >= today,
            ResearchMilestone.target_date <= today + timedelta(days=within_days),
        )
        .order_by(ResearchMilestone.target_date.asc())
    )
    return list(result.scalars().all())


async def upcoming_opportunity_deadlines(
    session: AsyncSession, user_id: uuid.UUID, today: date, within_days: int = 60
) -> list[ResearchOpportunity]:

    result = await session.execute(
        select(ResearchOpportunity)
        .where(
            ResearchOpportunity.user_id == user_id,
            ResearchOpportunity.status.in_(("interested", "shortlisted", "preparing")),
            ResearchOpportunity.submission_deadline.is_not(None),
            ResearchOpportunity.submission_deadline >= today,
            ResearchOpportunity.submission_deadline <= today + timedelta(days=within_days),
        )
        .order_by(ResearchOpportunity.submission_deadline.asc())
    )
    return list(result.scalars().all())
