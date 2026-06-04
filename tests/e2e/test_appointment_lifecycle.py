from datetime import datetime, timedelta, timezone
import pytest

from app.domain.value_objects.user_role import UserRole


def future_weekday_at(hour: int = 10) -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


@pytest.mark.asyncio
async def test_appointment_lifecycle_create_confirm_cancel(async_client, db_session, create_user, create_patient, create_doctor):
    admin = await create_user(
        db_session,
        email="admin.appointment@test.com",
        password="Password123!",
        role=UserRole.admin,
    )
    patient = await create_patient(
        db_session,
        email="patient.appointment@test.com",
        password="Password123!",
        first_name="Lucia",
        last_name="Torres",
        document_number="PAT-1000",
    )
    doctor = await create_doctor(
        db_session,
        email="doctor.appointment@test.com",
        password="Password123!",
        first_name="Esteban",
        last_name="Ortiz",
        specialty="Neurologia",
        license_number="MED-1000",
    )

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": admin.email, "password": "Password123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "patient_id": str(patient.id),
        "doctor_id": str(doctor.id),
        "scheduled_at": future_weekday_at().isoformat(),
        "duration_minutes": 30,
        "notes": "Consulta e2e",
    }

    create_response = await async_client.post(
        "/api/v1/appointments",
        headers=headers,
        json=payload,
    )
    assert create_response.status_code == 201

    appointment_id = create_response.json()["id"]

    confirm_response = await async_client.patch(
        f"/api/v1/appointments/{appointment_id}/confirm",
        headers=headers,
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "confirmed"

    cancel_response = await async_client.patch(
        f"/api/v1/appointments/{appointment_id}/cancel",
        headers=headers,
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"
