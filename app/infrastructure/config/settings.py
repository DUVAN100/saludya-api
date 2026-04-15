from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Base de datos ──────────────────────────────────────────────────────────
    # Supabase expone el connection string en:
    # Project Settings → Database → Connection string → URI
    # Ejemplo: postgresql+asyncpg://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
    database_url: str
    db_echo: bool = False          # True en desarrollo para ver queries SQL

    # ── JWT ────────────────────────────────────────────────────────────────────
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ── App ────────────────────────────────────────────────────────────────────
    app_name: str = "Health Appointments API"
    app_version: str = "0.1.0"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Instancia única de Settings cacheada con lru_cache.
    Evita releer el .env en cada request.
    """
    return Settings()


settings = get_settings()