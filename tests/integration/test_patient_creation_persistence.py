from datetime import date
from uuid import UUID
from sqlalchemy import select

import pytest

from app.infrastructure.persistence.models.patient_model import PatientModel


@pytest.mark.asyncio
async def test_register_patient_persists_data(async_client, db_session):
    payload = {
        "email": "newpatient@test.com",
        "password": "Password123!",
        "first_name": "Laura",
        "last_name": "Martinez",
        "birth_date": "1990-06-01",
        "phone": "3001234567",
        "document_number": "PAT-999",
        "document_type": "CC",
        "gender": "F",
        "address": "Calle 123",
    }

    response = await async_client.post("/api/v1/patients", json=payload)
    assert response.status_code == 201

    result = response.json()
    assert result["first_name"] == "Laura"
    assert result["document_number"] == "PAT-999"
    assert result["gender"] == "F"

    query = await db_session.execute(
        select(PatientModel).where(PatientModel.id == UUID(result["id"]))
    )
    stored_patient = query.scalar_one_or_none()
    assert stored_patient is not None
    assert stored_patient.document_number == "PAT-999"
    assert stored_patient.first_name == "Laura"
    assert stored_patient.user_id is not None
