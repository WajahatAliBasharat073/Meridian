from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    ai_settings,
    attempts,
    blocks,
    concepts,
    daily_recap,
    dashboard,
    goals,
    life_logs,
    problems,
    profile,
    questions,
    recommend,
    reflections,
    reviews,
    time_budgets,
    today,
    weekly_review,
)

settings = get_settings()

app = FastAPI(title="Meridian API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(today.router)
app.include_router(blocks.router)
app.include_router(attempts.router)
app.include_router(recommend.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)
app.include_router(problems.router)
app.include_router(profile.router)
app.include_router(daily_recap.router)
app.include_router(concepts.router)
app.include_router(questions.router)
app.include_router(goals.router)
app.include_router(time_budgets.router)
app.include_router(reflections.router)
app.include_router(weekly_review.router)
app.include_router(ai_settings.router)
app.include_router(life_logs.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
