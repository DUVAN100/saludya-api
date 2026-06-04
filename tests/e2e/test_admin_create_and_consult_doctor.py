from datetime import datetime, timedelta, timezone
import pytest

from app.domain.value_objects.user_role import UserRole


def future_weekday_at(hour: int = 10) -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


@pytest.mark.asyncio
async def test_admin_can_create_and_consult_doctor(async_client, db_session, create_user):
    admin = await create_user(
        db_session,
        email="admin.e2e@test.com",
        password="Password123!",
        role=UserRole.admin,
    )

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": admin.email, "password": "Password123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    doctor_payload = {
        "email": "e2e.doctor@test.com",
        "password": "Password123!",
        "first_name": "Martin",
        "last_name": "Rubio",
        "specialty": "Endocrinologia",
        "license_number": "MED-E2E-001",
        "phone": "3001112222",
        "consultation_duration": 30,
    }

    create_response = await async_client.post(
        "/api/v1/doctors",
        headers=headers,
        json=doctor_payload,
    )
    assert create_response.status_code == 201

    doctor_id = create_response.json()["id"]
    doctor_response = await async_client.get(
        f"/api/v1/doctors/{doctor_id}",
        headers=headers,
    )
    assert doctor_response.status_code == 200
    assert doctor_response.json()["license_number"] == "MED-E2E-001"
