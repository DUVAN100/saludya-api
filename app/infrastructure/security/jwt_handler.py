from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.application.dtos.auth_dto import TokenPayloadDTO
from app.domain.exceptions.domain_exceptions import InvalidCredentialsException
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.config.settings import settings


class JWTHandler:
    """
    Adaptador de seguridad — genera y valida tokens JWT usando python-jose.
    """

    def create_access_token(self, payload: dict) -> str:
        """
        Genera un JWT firmado con HS256.
        Agrega 'exp' e 'iat' automáticamente.
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.jwt_expire_minutes)

        claims = {
            **payload,
            "iat": now,
            "exp": expire,
        }
        return jwt.encode(
            claims,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def decode_access_token(self, token: str) -> TokenPayloadDTO:
        """
        Decodifica y valida un JWT.
        Lanza InvalidCredentialsException si el token es inválido o expiró.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            user_id: str | None = payload.get("sub")
            role_value: str | None = payload.get("role")

            if not user_id or not role_value:
                raise InvalidCredentialsException()

            return TokenPayloadDTO(
                sub=user_id,
                role=UserRole(role_value),
            )

        except JWTError:
            raise InvalidCredentialsException()