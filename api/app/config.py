from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server-side configuration. GROQ_API_KEY never leaves this process —
    it is read here and nowhere else touches the browser (build prompt 2.1)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://meridian:meridian@localhost:5432/meridian"

    # Legacy HS256 shared-secret verification (older Supabase projects).
    supabase_jwt_secret: str = ""
    # Needed for ES256/RS256 verification via the project's JWKS endpoint
    # (current Supabase default — "JWT Signing Keys"). e.g.
    # https://<ref>.supabase.co
    supabase_url: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    daily_token_budget: int = 200_000

    # Prayer-time anchor — Islamabad by default (design doc 5).
    latitude: float = 33.6844
    longitude: float = 73.0479
    timezone: str = "Asia/Karachi"

    cors_origins: str = "http://localhost:3000"

    daily_review_cap: int = 12

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
