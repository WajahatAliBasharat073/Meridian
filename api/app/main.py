from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import attempts, blocks, dashboard, recommend, reviews, today

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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
