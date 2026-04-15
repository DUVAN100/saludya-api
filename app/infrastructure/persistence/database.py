from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.config.settings import settings


# ── Engine ─────────────────────────────────────────────────────────────────────
# pool_pre_ping=True valida la conexión antes de usarla —
# importante en Supabase donde conexiones idle pueden cerrarse por el pooler.
print("🔗 DATABASE_URL final:", settings.database_url)
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# ── Session factory ────────────────────────────────────────────────────────────
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # evita lazy-load tras commit en contexto async
    autoflush=False,
    autocommit=False,
)


# ── Base declarativa para todos los modelos ────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency para FastAPI ────────────────────────────────────────────────────
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Inyecta una sesión de base de datos por request.
    Hace commit al final o rollback automático si hay excepción.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise