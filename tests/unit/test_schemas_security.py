from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.adapters.http.schemas.appointment_schema import CreateAppointmentRequest
from app.adapters.http.schemas.auth_schema import LoginRequest, TokenResponse
from app.adapters.http.schemas.doctor_schema import CreateDoctorRequest
from app.adapters.http.schemas.patient_schema import RegisterPatientRequest
from app.domain.exceptions.domain_exceptions import InvalidCredentialsException
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import PasswordHasher


def future_aware_datetime() -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=10, minute=0, second=0, microsecond=0)


def test_login_request_and_token_response_models():
    request = LoginRequest(email="user@example.com", password="Password123!")
    response = TokenResponse(access_token="token")

    assert request.email == "user@example.com"
    assert response.token_type == "bearer"


def test_patient_schema_validates_email_password_document_and_gender():
    valid = RegisterPatientRequest(
        email="patient@example.com",
        password="Password123!",
        first_name="Ana",
        last_name="Lopez",
        document_type="CC",
        gender="F",
    )

    assert valid.first_name == "Ana"

    with pytest.raises(ValidationError):
        RegisterPatientRequest(
            email="bad-email",
            password="short",
            first_name="",
            last_name="Lopez",
            document_type="BAD",
            gender="X",
        )


def test_doctor_schema_validates_required_ranges():
    valid = CreateDoctorRequest(
        email="doctor@example.com",
        password="Password123!",
        first_name="Carlos",
        last_name="Perez",
        specialty="Cardiologia",
        license_number="MED-1",
        consultation_duration=30,
    )

    assert valid.consultation_duration == 30

    with pytest.raises(ValidationError):
        CreateDoctorRequest(
            email="doctor@example.com",
            password="Password123!",
            first_name="Carlos",
            last_name="Perez",
            specialty="Cardiologia",
            license_number="MED-1",
            consultation_duration=5,
        )


def test_appointment_schema_requires_timezone_and_valid_duration():
    valid = CreateAppointmentRequest(
        patient_id=uuid4(),
        doctor_id=uuid4(),
        scheduled_at=future_aware_datetime(),
        duration_minutes=30,
    )

    assert valid.scheduled_at.tzinfo is not None

    with pytest.raises(ValidationError):
        CreateAppointmentRequest(
            patient_id=uuid4(),
            doctor_id=uuid4(),
            scheduled_at=datetime.now() + timedelta(days=1),
            duration_minutes=30,
        )

    with pytest.raises(ValidationError):
        CreateAppointmentRequest(
            patient_id=uuid4(),
            doctor_id=uuid4(),
            scheduled_at=future_aware_datetime(),
            duration_minutes=121,
        )


def test_password_hasher_hashes_and_verifies_passwords():
    hasher = PasswordHasher()

    hashed = hasher.hash("Password123!")

    assert hashed != "Password123!"
    assert hasher.verify("Password123!", hashed) is True
    assert hasher.verify("WrongPassword!", hashed) is False
    assert hasher.hash("Password123!") != hashed


def test_jwt_handler_creates_and_decodes_token():
    handler = JWTHandler()
    user_id = str(uuid4())

    token = handler.create_access_token({"sub": user_id, "role": UserRole.admin.value})
    payload = handler.decode_access_token(token)

    assert payload.sub == user_id
    assert payload.role == UserRole.admin


@pytest.mark.parametrize("payload", [{}, {"sub": str(uuid4())}, {"role": "admin"}])
def test_jwt_handler_rejects_missing_required_claims(payload):
    handler = JWTHandler()
    token = handler.create_access_token(payload)

    with pytest.raises(InvalidCredentialsException):
        handler.decode_access_token(token)


def test_jwt_handler_rejects_invalid_token():
    with pytest.raises(InvalidCredentialsException):
        JWTHandler().decode_access_token("not-a-valid-token")
