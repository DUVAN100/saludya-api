from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select

import pytest

from app.domain.value_objects.user_role import UserRole
from app.infrastructure.persistence.models.appointment_model import AppointmentModel
from app.infrastructure.persistence.models.patient_model import PatientModel


def future_weekday_at(hour: int = 10) -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


@pytest.mark.asyncio
async def test_create_appointment_and_query_by_patient(async_client, db_session, create_patient, create_doctor, auth_header_factory):
    patient = await create_patient(
        db_session,
        email="patient2@test.com",
        password="Password123!",
        first_name="Laura",
        last_name="Sanchez",
        document_number="PAT-002",
    )
    doctor = await create_doctor(
        db_session,
        email="doctor2@test.com",
        password="Password123!",
        first_name="Jose",
        last_name="Medina",
        specialty="Dermatologia",
        license_number="MED-002",
    )

    token = auth_header_factory(role=UserRole.patient, sub=str(patient.user_id))["Authorization"]
    scheduled_at = future_weekday_at().isoformat()
    response = await async_client.post(
        "/api/v1/appointments",
        headers={"Authorization": token},
        json={
            "patient_id": str(patient.id),
            "doctor_id": str(doctor.id),
            "scheduled_at": scheduled_at,
            "duration_minutes": 30,
            "notes": "Consulta de seguimiento",
        },
    )

    assert response.status_code == 201
    appointment_id = response.json()["id"]

    query = await db_session.execute(
        select(AppointmentModel).where(AppointmentModel.id == UUID(appointment_id))
    )
    stored_appointment = query.scalar_one_or_none()
    assert stored_appointment is not None
    assert stored_appointment.patient_id == patient.id
    assert stored_appointment.doctor_id == doctor.id

    follow_up = await async_client.get(
        f"/api/v1/appointments/patient/{patient.id}",
        headers={"Authorization": token},
    )
    assert follow_up.status_code == 200
    assert len(follow_up.json()) == 1
    assert follow_up.json()[0]["id"] == appointment_id
