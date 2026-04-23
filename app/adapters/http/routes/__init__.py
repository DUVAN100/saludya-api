from .auth_routes import router as auth_router
from .patients_routes import router as patients_router
from .doctors_routes import router as doctors_router
from .appointments_routes import router as appointments_router

__all__ = [
    "auth_router",
    "patients_router",
    "doctors_router",
    "appointments_router",
]