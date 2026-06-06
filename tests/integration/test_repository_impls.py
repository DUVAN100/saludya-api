from datetime import datetime, time, timedelta, timezone
from uuid import uuid4

import pytest

from datetime import datetime, time, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.entities.appointment import Appointment
from app.domain.entities.doctor import Doctor, DoctorAvailability
from app.domain.entities.patient import Patient
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.appointment_status import AppointmentStatus
from app.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.persistence.repositories.patient_repository_impl import PatientRepositoryImpl
from app.infrastructure.persistence.repositories.doctor_repository_impl import DoctorRepositoryImpl
from app.infrastructure.persistence.repositories.appointment_repository_impl import AppointmentRepositoryImpl


def future_weekday_at(hour: int = 10) -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


def make_user(role: UserRole = UserRole.patient, active: bool = True) -> User:
    return User(
        email=Email(f"{role.value}-{uuid4()}@example.com"),
        password_hash="hashed:Password123!",
        role=role,
        is_active=active,
    )


def make_patient(user_id=None) -> Patient:
    return Patient(
        user_id=user_id or uuid4(),
        first_name="Ana",
        last_name="Paciente",
        document_number=f"DOC-{uuid4()}",
    )


def make_doctor(scheduled_at: datetime | None = None) -> Doctor:
    doctor = Doctor(
        user_id=uuid4(),
        first_name="Carlos",
        last_name="Medico",
        specialty="Cardiologia",
        license_number=f"MED-{uuid4()}",
        phone="123456789",
    )
    if scheduled_at:
        doctor.availability.append(
            DoctorAvailability(
                doctor_id=doctor.id,
                day_of_week=scheduled_at.isoweekday(),
                start_time=time(8, 0),
                end_time=time(17, 0),
            )
        )
    return doctor


def make_appointment(patient_id, doctor_id, scheduled_at):
    return Appointment.create(
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_at=scheduled_at,
        notes="Consulta de prueba",
    )


@pytest.mark.asyncio
async def test_user_repository_impl_crud(db_session):
    repo = UserRepositoryImpl(db_session)
    user = make_user()

    saved = await repo.save(user)
    assert saved.id == user.id
    assert await repo.exists_by_email(user.email.value)

    found_by_id = await repo.find_by_id(user.id)
    assert found_by_id is not None
    assert found_by_id.email.value == user.email.value

    found_by_email = await repo.find_by_email(user.email.value)
    assert found_by_email is not None
    assert found_by_email.id == user.id

    user.is_active = False
    user.password_hash = "new-hash"
    updated = await repo.update(user)
    assert updated.password_hash == "new-hash"
    assert not updated.is_active


@pytest.mark.asyncio
async def test_patient_repository_impl_crud(db_session):
    repo = PatientRepositoryImpl(db_session)
    patient = make_patient()

    saved = await repo.save(patient)
    assert saved.id == patient.id

    by_id = await repo.find_by_id(patient.id)
    assert by_id is not None
    assert by_id.document_number == patient.document_number

    by_user = await repo.find_by_user_id(patient.user_id)
    assert by_user is not None

    by_document = await repo.find_by_document_number(patient.document_number)
    assert by_document is not None

    assert await repo.exists_by_document_number(patient.document_number)

    patient.phone = "987654321"
    patient.address = "Calle Falsa 123"
    updated = await repo.update(patient)
    assert updated.phone == "987654321"
    assert updated.address == "Calle Falsa 123"

    all_patients = await repo.find_all()
    assert any(p.id == patient.id for p in all_patients)


@pytest.mark.asyncio
async def test_doctor_repository_impl_crud(db_session):
    repo = DoctorRepositoryImpl(db_session)
    scheduled_at = future_weekday_at()
    doctor = make_doctor(scheduled_at)

    saved = await repo.save(doctor)
    assert saved.id == doctor.id

    availability = doctor.availability[0]
    saved_avail = await repo.save_availability(availability)
    assert saved_avail.id == availability.id

    by_id = await repo.find_by_id(doctor.id)
    assert by_id is not None
    assert by_id.license_number == doctor.license_number

    by_id_with_avail = await repo.find_by_id_with_availability(doctor.id)
    assert by_id_with_avail is not None
    assert len(by_id_with_avail.availability) == 1

    assert await repo.exists_by_license_number(doctor.license_number)

    updated_doctor = doctor
    updated_doctor.phone = "5551234"
    updated_doctor.specialty = "Dermatologia"
    await repo.update(updated_doctor)

    by_specialty = await repo.find_by_specialty("Dermatologia")
    assert len(by_specialty) == 1

    all_doctors = await repo.find_all()
    assert any(d.id == doctor.id for d in all_doctors)


@pytest.mark.asyncio
async def test_appointment_repository_impl_crud(db_session):
    repo = AppointmentRepositoryImpl(db_session)
    scheduled_at = future_weekday_at()
    appointment = make_appointment(uuid4(), uuid4(), scheduled_at)

    saved = await repo.save(appointment)
    assert saved.id == appointment.id

    by_id = await repo.find_by_id(appointment.id)
    assert by_id is not None

    by_patient = await repo.find_by_patient_id(appointment.patient_id)
    assert len(by_patient) == 1

    by_doctor = await repo.find_by_doctor_id(appointment.doctor_id)
    assert len(by_doctor) == 1

    start = scheduled_at - timedelta(hours=1)
    end = scheduled_at + timedelta(hours=1)
    by_range = await repo.find_by_doctor_and_date_range(appointment.doctor_id, start, end)
    assert len(by_range) == 1

    assert await repo.exists_slot_taken(appointment.doctor_id, appointment.scheduled_at)

    appointment.confirm()
    appointment.notes = "Cambio de nota"
    updated = await repo.update(appointment)
    assert updated.status == AppointmentStatus.CONFIRMED
    assert updated.notes == "Cambio de nota"

    all_appointments = await repo.find_all(AppointmentStatus.CONFIRMED)
    assert len(all_appointments) == 1

    assert await repo.find_by_id(uuid4()) is None
