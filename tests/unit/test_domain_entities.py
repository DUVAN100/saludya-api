from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.entities.appointment import Appointment
from app.domain.entities.doctor import Doctor, DoctorAvailability
from app.domain.entities.patient import Patient
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    AppointmentInThePastException,
    AppointmentOutsideWorkingHoursException,
    InvalidStatusTransitionException,
)
from app.domain.value_objects.appointment_status import AppointmentStatus
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole


def future_weekday_at(hour: int = 10) -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


def test_email_accepts_valid_address():
    email = Email("user@example.com")

    assert email.value == "user@example.com"
    assert str(email) == "user@example.com"


@pytest.mark.parametrize("value", ["", "invalid", "missing-at.com", "a@b"])
def test_email_rejects_invalid_address(value):
    with pytest.raises(ValueError):
        Email(value)


def test_user_role_values_are_expected():
    assert UserRole.admin.value == "admin"
    assert UserRole.doctor.value == "doctor"
    assert UserRole.patient.value == "patient"


def test_user_activation_and_role_helpers_update_state():
    user = User(email=Email("admin@example.com"), password_hash="hash", role=UserRole.admin)
    original_updated_at = user.updated_at

    user.deactivate()

    assert user.is_active is False
    assert user.updated_at >= original_updated_at
    assert user.is_admin() is True
    assert user.is_doctor() is False
    assert user.is_patient() is False

    user.activate()

    assert user.is_active is True


def test_patient_full_name_and_age():
    patient = Patient(
        user_id=uuid4(),
        first_name="Ana",
        last_name="Lopez",
        birth_date=date(2000, 1, 1),
    )

    assert patient.full_name == "Ana Lopez"
    assert patient.age is not None
    assert patient.age >= 25


def test_patient_age_is_none_without_birth_date():
    patient = Patient(user_id=uuid4(), first_name="Ana", last_name="Lopez")

    assert patient.age is None


def test_doctor_availability_covers_active_time_range():
    availability = DoctorAvailability(
        doctor_id=uuid4(),
        day_of_week=1,
        start_time=time(8, 0),
        end_time=time(17, 0),
    )

    assert availability.covers(time(8, 0)) is True
    assert availability.covers(time(16, 59)) is True
    assert availability.covers(time(17, 0)) is False


def test_doctor_availability_ignores_inactive_slot():
    availability = DoctorAvailability(
        doctor_id=uuid4(),
        day_of_week=1,
        start_time=time(8, 0),
        end_time=time(17, 0),
        is_active=False,
    )

    assert availability.covers(time(10, 0)) is False


def test_doctor_full_name_and_availability():
    doctor_id = uuid4()
    scheduled_at = future_weekday_at()
    doctor = Doctor(
        user_id=uuid4(),
        first_name="Carlos",
        last_name="Perez",
        specialty="Cardiologia",
        license_number="MED-1",
        availability=[
            DoctorAvailability(
                doctor_id=doctor_id,
                day_of_week=scheduled_at.isoweekday(),
                start_time=time(8, 0),
                end_time=time(17, 0),
            )
        ],
    )

    assert doctor.full_name == "Dr. Carlos Perez"
    assert doctor.is_available_at(scheduled_at) is True
    assert doctor.is_available_at(scheduled_at.replace(hour=18)) is False


def test_appointment_status_transitions():
    assert AppointmentStatus.PENDING.can_transition_to(AppointmentStatus.CONFIRMED)
    assert AppointmentStatus.PENDING.can_transition_to(AppointmentStatus.CANCELLED)
    assert AppointmentStatus.CONFIRMED.can_transition_to(AppointmentStatus.COMPLETED)
    assert AppointmentStatus.CONFIRMED.can_transition_to(AppointmentStatus.NO_SHOW)
    assert not AppointmentStatus.CANCELLED.can_transition_to(AppointmentStatus.CONFIRMED)


def test_appointment_create_confirm_cancel_and_active_state():
    appointment = Appointment.create(
        patient_id=uuid4(),
        doctor_id=uuid4(),
        scheduled_at=future_weekday_at(),
    )

    assert appointment.status == AppointmentStatus.PENDING
    assert appointment.is_active is True

    appointment.confirm()
    assert appointment.status == AppointmentStatus.CONFIRMED
    assert appointment.is_active is True

    appointment.cancel()
    assert appointment.status == AppointmentStatus.CANCELLED
    assert appointment.is_active is False


def test_appointment_complete_and_no_show_from_confirmed():
    appointment = Appointment.create(uuid4(), uuid4(), future_weekday_at())
    appointment.confirm()

    appointment.complete()

    assert appointment.status == AppointmentStatus.COMPLETED
    assert appointment.is_active is False

    other = Appointment.create(uuid4(), uuid4(), future_weekday_at())
    other.confirm()
    other.mark_no_show()
    assert other.status == AppointmentStatus.NO_SHOW


def test_appointment_rejects_invalid_transition():
    appointment = Appointment.create(uuid4(), uuid4(), future_weekday_at())
    appointment.cancel()

    with pytest.raises(InvalidStatusTransitionException):
        appointment.confirm()


def test_appointment_rejects_naive_datetime():
    with pytest.raises(ValueError):
        Appointment.create(uuid4(), uuid4(), datetime.now() + timedelta(days=1))


def test_appointment_rejects_past_datetime():
    with pytest.raises(AppointmentInThePastException):
        Appointment.create(uuid4(), uuid4(), datetime.now(timezone.utc) - timedelta(days=1))


def test_appointment_rejects_weekend_and_outside_working_hours():
    saturday = datetime.now(timezone.utc) + timedelta(days=1)
    while saturday.isoweekday() != 6:
        saturday += timedelta(days=1)
    saturday = saturday.replace(hour=10, minute=0, second=0, microsecond=0)

    with pytest.raises(AppointmentOutsideWorkingHoursException):
        Appointment.create(uuid4(), uuid4(), saturday)

    with pytest.raises(AppointmentOutsideWorkingHoursException):
        Appointment.create(uuid4(), uuid4(), future_weekday_at(hour=18))
