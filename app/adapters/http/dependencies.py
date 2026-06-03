from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dtos.auth_dto import TokenPayloadDTO
from app.domain.exceptions.domain_exceptions import InvalidCredentialsException
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.security.jwt_handler import JWTHandler

_bearer = HTTPBearer()
_jwt_handler = JWTHandler()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenPayloadDTO:
    """
    Dependency que extrae y valida el JWT del header Authorization.
    Inyectable en cualquier endpoint que requiera autenticación.
    """
    try:
        return _jwt_handler.decode_access_token(credentials.credentials)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(
    current_user: TokenPayloadDTO = Depends(get_current_user),
) -> TokenPayloadDTO:
    """Solo permite acceso a usuarios con rol admin."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores",
        )
    return current_user


def require_doctor(
    current_user: TokenPayloadDTO = Depends(get_current_user),
) -> TokenPayloadDTO:
    """Solo permite acceso a médicos."""
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a médicos",
        )
    return current_user


def require_admin_or_doctor(
    current_user: TokenPayloadDTO = Depends(get_current_user),
) -> TokenPayloadDTO:
    if current_user.role not in {UserRole.admin, UserRole.doctor}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a médicos y administradores",
        )
    return current_user