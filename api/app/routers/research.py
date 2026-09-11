from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.engines.research import (
    MilestoneSummary,
    OpportunitySummary,
    TopicSummary,
    build_at_a_glance,
)
from app.logging import get_logger
from app.models.research import (
    ResearchExperiment,
    ResearchMilestone,
    ResearchNote,
    ResearchOpportunity,
    ResearchPaper,
    ResearchTopic,
)
from app.repositories import goals as goals_repo
from app.repositories import research as research_repo
from app.schemas import (
    GoalOut,
    ResearchAtAGlanceOut,
    ResearchExperimentCreate,
    ResearchExperimentOut,
    ResearchExperimentUpdate,
    ResearchMilestoneCreate,
    ResearchMilestoneOut,
    ResearchMilestoneUpdate,
    ResearchNoteCreate,
    ResearchNoteOut,
    ResearchOpportunityCreate,
    ResearchOpportunityOut,
    ResearchOpportunityUpdate,
    ResearchPaperCreate,
    ResearchPaperOut,
    ResearchPaperUpdate,
    ResearchTopicCreate,
    ResearchTopicOut,
    ResearchTopicUpdate,
)

log = get_logger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


def _topic_out(t: ResearchTopic) -> ResearchTopicOut:
    return ResearchTopicOut(
        id=t.id, title=t.title, description=t.description, status=t.status, current_blocker=t.current_blocker
    )


def _paper_out(p: ResearchPaper) -> ResearchPaperOut:
    return ResearchPaperOut(
        id=p.id, topic_id=p.topic_id, title=p.title, authors=p.authors, year=p.year, venue=p.venue,
        url=p.url, status=p.status, summary=p.summary, relevance_note=p.relevance_note,
    )


def _note_out(n: ResearchNote) -> ResearchNoteOut:
    return ResearchNoteOut(id=n.id, topic_id=n.topic_id, paper_id=n.paper_id, kind=n.kind, content=n.content)


def _experiment_out(e: ResearchExperiment) -> ResearchExperimentOut:
    return ResearchExperimentOut(
        id=e.id, topic_id=e.topic_id, title=e.title, description=e.description, dataset=e.dataset,
        methodology_note=e.methodology_note, status=e.status, result_summary=e.result_summary,
        started_date=e.started_date, completed_date=e.completed_date,
    )


def _milestone_out(m: ResearchMilestone) -> ResearchMilestoneOut:
    return ResearchMilestoneOut(
        id=m.id, topic_id=m.topic_id, title=m.title, description=m.description,
        target_date=m.target_date, status=m.status,
    )


def _opportunity_out(o: ResearchOpportunity) -> ResearchOpportunityOut:
    return ResearchOpportunityOut(
        id=o.id, venue_name=o.venue_name, venue_type=o.venue_type, research_area=o.research_area,
        submission_deadline=o.submission_deadline, notification_date=o.notification_date,
        event_date=o.event_date, location=o.location, links=o.links, submission_type=o.submission_type,
        relevance=o.relevance, priority=o.priority, status=o.status, notes=o.notes,
    )


# ----------------------------------------------------------------- topics


@router.get("/topics", response_model=list[ResearchTopicOut])
async def list_topics(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[ResearchTopicOut]:
    return [_topic_out(t) for t in await research_repo.list_topics(session, user_id)]


@router.post("/topics", response_model=ResearchTopicOut, status_code=status.HTTP_201_CREATED)
async def create_topic(
    payload: ResearchTopicCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchTopicOut:
    topic = await research_repo.create_topic(session, user_id, payload.title, payload.description)
    return _topic_out(topic)


@router.patch("/topics/{topic_id}", response_model=ResearchTopicOut)
async def update_topic(
    topic_id: int,
    payload: ResearchTopicUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchTopicOut:
    topic = await research_repo.update_topic(
        session, user_id, topic_id, payload.model_dump(exclude_unset=True)
    )
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    return _topic_out(topic)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await research_repo.delete_topic(session, user_id, topic_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")


# ----------------------------------------------------------------- papers


@router.get("/papers", response_model=list[ResearchPaperOut])
async def list_papers(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    topic_id: int | None = None,
    status_filter: str | None = None,
) -> list[ResearchPaperOut]:
    papers = await research_repo.list_papers(session, user_id, topic_id, status_filter)
    return [_paper_out(p) for p in papers]


@router.post("/papers", response_model=ResearchPaperOut, status_code=status.HTTP_201_CREATED)
async def create_paper(
    payload: ResearchPaperCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchPaperOut:
    paper = await research_repo.create_paper(session, user_id, payload.model_dump())
    return _paper_out(paper)


@router.patch("/papers/{paper_id}", response_model=ResearchPaperOut)
async def update_paper(
    paper_id: int,
    payload: ResearchPaperUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchPaperOut:
    paper = await research_repo.update_paper(
        session, user_id, paper_id, payload.model_dump(exclude_unset=True)
    )
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    return _paper_out(paper)


@router.delete("/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await research_repo.delete_paper(session, user_id, paper_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")


# ------------------------------------------------------------------ notes


@router.get("/notes", response_model=list[ResearchNoteOut])
async def list_notes(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    topic_id: int | None = None,
    paper_id: int | None = None,
    kind: str | None = None,
) -> list[ResearchNoteOut]:
    notes = await research_repo.list_notes(session, user_id, topic_id, paper_id, kind)
    return [_note_out(n) for n in notes]


@router.post("/notes", response_model=ResearchNoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: ResearchNoteCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchNoteOut:
    note = await research_repo.create_note(session, user_id, payload.model_dump())
    return _note_out(note)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await research_repo.delete_note(session, user_id, note_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


# ------------------------------------------------------------ experiments


@router.get("/experiments", response_model=list[ResearchExperimentOut])
async def list_experiments(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    topic_id: int | None = None,
) -> list[ResearchExperimentOut]:
    experiments = await research_repo.list_experiments(session, user_id, topic_id)
    return [_experiment_out(e) for e in experiments]


@router.post("/experiments", response_model=ResearchExperimentOut, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    payload: ResearchExperimentCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchExperimentOut:
    experiment = await research_repo.create_experiment(session, user_id, payload.model_dump())
    return _experiment_out(experiment)


@router.patch("/experiments/{experiment_id}", response_model=ResearchExperimentOut)
async def update_experiment(
    experiment_id: int,
    payload: ResearchExperimentUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchExperimentOut:
    experiment = await research_repo.update_experiment(
        session, user_id, experiment_id, payload.model_dump(exclude_unset=True)
    )
    if experiment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
    return _experiment_out(experiment)


@router.delete("/experiments/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
    experiment_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await research_repo.delete_experiment(session, user_id, experiment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")


# ------------------------------------------------------------- milestones


@router.get("/milestones", response_model=list[ResearchMilestoneOut])
async def list_milestones(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    topic_id: int | None = None,
) -> list[ResearchMilestoneOut]:
    milestones = await research_repo.list_milestones(session, user_id, topic_id)
    return [_milestone_out(m) for m in milestones]


@router.post("/milestones", response_model=ResearchMilestoneOut, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    payload: ResearchMilestoneCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchMilestoneOut:
    milestone = await research_repo.create_milestone(session, user_id, payload.model_dump())
    return _milestone_out(milestone)


@router.patch("/milestones/{milestone_id}", response_model=ResearchMilestoneOut)
async def update_milestone(
    milestone_id: int,
    payload: ResearchMilestoneUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchMilestoneOut:
    milestone = await research_repo.update_milestone(
        session, user_id, milestone_id, payload.model_dump(exclude_unset=True)
    )
    if milestone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return _milestone_out(milestone)


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await research_repo.delete_milestone(session, user_id, milestone_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")


# ---------------------------------------------------------- opportunities


@router.get("/opportunities", response_model=list[ResearchOpportunityOut])
async def list_opportunities(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    status_filter: str | None = None,
) -> list[ResearchOpportunityOut]:
    opportunities = await research_repo.list_opportunities(session, user_id, status_filter)
    return [_opportunity_out(o) for o in opportunities]


@router.post("/opportunities", response_model=ResearchOpportunityOut, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    payload: ResearchOpportunityCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchOpportunityOut:
    opportunity = await research_repo.create_opportunity(session, user_id, payload.model_dump())
    log.info("research_opportunity_created", user_id=str(user_id), venue=payload.venue_name)
    return _opportunity_out(opportunity)


@router.patch("/opportunities/{opportunity_id}", response_model=ResearchOpportunityOut)
async def update_opportunity(
    opportunity_id: int,
    payload: ResearchOpportunityUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchOpportunityOut:
    opportunity = await research_repo.update_opportunity(
        session, user_id, opportunity_id, payload.model_dump(exclude_unset=True)
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return _opportunity_out(opportunity)


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await research_repo.delete_opportunity(session, user_id, opportunity_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")


@router.post("/opportunities/{opportunity_id}/add-to-goals", response_model=GoalOut)
async def add_opportunity_to_goals(
    opportunity_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> GoalOut:
    """Turns a tracked opportunity into a real Goal -- title and
    target_date are derived from the opportunity, never re-typed."""
    opportunity = await research_repo.get_opportunity(session, user_id, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    goal = await goals_repo.create_goal(
        session,
        user_id,
        title=f"Submit to {opportunity.venue_name}",
        description=f"Research target derived from a tracked {opportunity.venue_type}.",
        category=None,
        target_date=opportunity.submission_deadline,
    )
    log.info("research_opportunity_added_to_goals", user_id=str(user_id), opportunity_id=opportunity_id)
    return GoalOut(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        category=goal.category,
        target_date=goal.target_date,
        progress_pct=goal.progress_pct,
        status=goal.status,
        minutes_logged=None,
        finance_goal_id=None,
        linked_finance_goal=None,
    )


# --------------------------------------------------------- at-a-glance


@router.get("/at-a-glance", response_model=ResearchAtAGlanceOut)
async def get_at_a_glance(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ResearchAtAGlanceOut:
    today = date.today()
    active_topics = [
        TopicSummary(id=t.id, title=t.title, current_blocker=t.current_blocker)
        for t in await research_repo.list_topics(session, user_id)
        if t.status == "active"
    ]
    papers_to_read = await research_repo.count_papers_to_read(session, user_id)
    milestones = [
        MilestoneSummary(id=m.id, title=m.title, target_date=m.target_date)
        for m in await research_repo.upcoming_milestones(session, user_id, today)
        if m.target_date is not None
    ]
    opportunities = [
        OpportunitySummary(id=o.id, venue_name=o.venue_name, submission_deadline=o.submission_deadline)
        for o in await research_repo.upcoming_opportunity_deadlines(session, user_id, today)
        if o.submission_deadline is not None
    ]

    glance = build_at_a_glance(active_topics, papers_to_read, milestones, opportunities, today)

    active_topic_out = None
    if glance.active_topic is not None:
        topic_row = await research_repo.get_topic(session, user_id, glance.active_topic.id)
        active_topic_out = _topic_out(topic_row) if topic_row else None

    next_milestone_out = None
    if glance.next_milestone is not None:
        milestone_row = await research_repo.get_milestone(session, user_id, glance.next_milestone.id)
        next_milestone_out = _milestone_out(milestone_row) if milestone_row else None

    next_opportunity_out = None
    if glance.next_opportunity is not None:
        opp_row = await research_repo.get_opportunity(session, user_id, glance.next_opportunity.id)
        next_opportunity_out = _opportunity_out(opp_row) if opp_row else None

    return ResearchAtAGlanceOut(
        active_topic=active_topic_out,
        papers_to_read_count=glance.papers_to_read_count,
        next_milestone=next_milestone_out,
        next_opportunity=next_opportunity_out,
        highlights=glance.highlights,
    )
