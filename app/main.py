from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.http.exception_handlers import register_exception_handlers
from app.adapters.http.routes import (
    appointments_router,
    auth_router,
    doctors_router,
    patients_router,
)
from app.infrastructure.config.settings import settings


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de arranque y cierre de la aplicación."""
    yield


# ── Aplicación ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ─────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ────────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth_router,         prefix=API_PREFIX)
app.include_router(patients_router,     prefix=API_PREFIX)
app.include_router(doctors_router,      prefix=API_PREFIX)
app.include_router(appointments_router, prefix=API_PREFIX)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "version": settings.app_version}