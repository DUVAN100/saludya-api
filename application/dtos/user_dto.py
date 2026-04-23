from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.user_role import UserRole


@dataclass(frozen=True)
class UserDTO:
    """
    DTO de salida — lo que la aplicación devuelve al adaptador HTTP.
    Nunca expone password_hash.
    """
    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class CreateUserDTO:
    """DTO de entrada para crear un usuario."""
    email: str
    password: str          # contraseña en texto plano — la infraestructura la hashea
    role: UserRole