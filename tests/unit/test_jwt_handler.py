from datetime import datetime, timedelta, timezone

import pytest

from app.infrastructure.security.jwt_handler import JWTHandler
from app.application.dtos.auth_dto import TokenPayloadDTO
from app.domain.exceptions.domain_exceptions import InvalidCredentialsException
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.config.settings import settings


def test_create_access_token_and_decode_payload():
    handler = JWTHandler()

    token = handler.create_access_token({"sub": "user-id", "role": UserRole.patient.value})

    assert isinstance(token, str)
    assert token.count(".") == 2

    payload = handler.decode_access_token(token)

    assert isinstance(payload, TokenPayloadDTO)
    assert payload.sub == "user-id"
    assert payload.role == UserRole.patient


def test_decode_access_token_missing_claims_raises_invalid_credentials():
    handler = JWTHandler()
    invalid_token = handler.create_access_token({"sub": "user-id"})

    with pytest.raises(InvalidCredentialsException):
        handler.decode_access_token(invalid_token)


def test_decode_access_token_invalid_token_raises_invalid_credentials():
    handler = JWTHandler()

    with pytest.raises(InvalidCredentialsException):
        handler.decode_access_token("not-a-valid-jwt")
