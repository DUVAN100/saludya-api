from app.domain.value_objects.user_role import UserRole
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import PasswordHasher
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select

import pytest


@pytest.mark.asyncio
async def test_login_and_jwt_validation(async_client, db_session):
    user = UserModel(
        id=uuid4(),
        email="admin@test.com",
        password_hash=PasswordHasher().hash("Password123!"),
        role=UserRole.admin.value,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "Password123!"},
    )
    assert response.status_code == 200

    payload = JWTHandler().decode_access_token(response.json()["access_token"])
    assert payload.sub == str(user.id)
    assert payload.role == UserRole.admin

    protected = await async_client.get(
        "/api/v1/patients",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert protected.status_code == 200
