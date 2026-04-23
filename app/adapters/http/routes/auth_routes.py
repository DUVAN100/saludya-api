from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.http.schemas.auth_schema import LoginRequest, TokenResponse
from app.application.dtos.auth_dto import LoginDTO
from app.application.use_cases.auth.login import LoginUseCase
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import PasswordHasher

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_use_case(session: AsyncSession) -> LoginUseCase:
    return LoginUseCase(
        user_repository=UserRepositoryImpl(session),
        password_hasher=PasswordHasher(),
        token_service=JWTHandler(),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    status_code=200,
)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    use_case = _build_use_case(session)
    result = await use_case.execute(LoginDTO(email=body.email, password=body.password))
    return TokenResponse(access_token=result.access_token)