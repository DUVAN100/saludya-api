from dataclasses import dataclass

from app.domain.value_objects.user_role import UserRole


@dataclass(frozen=True)
class LoginDTO:
    """DTO de entrada — credenciales del usuario."""
    email: str
    password: str


@dataclass(frozen=True)
class TokenDTO:
    """DTO de salida — tokens JWT generados tras el login."""
    access_token: str
    token_type: str = "bearer"


@dataclass(frozen=True)
class TokenPayloadDTO:
    """DTO interno — payload decodificado del JWT."""
    sub: str          # user_id como string
    role: UserRole