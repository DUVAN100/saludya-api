import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.appointment import Appointment
from app.domain.value_objects.appointment_status import AppointmentStatus
from app.domain.exceptions.domain_exceptions import (
    InvalidStatusTransitionException,
    AppointmentInThePastException,
    AppointmentOutsideWorkingHoursException,
)


def future_weekday(hour: int = 10) -> datetime:
    dt = datetime.now(timezone.utc) + timedelta(days=1)
    while dt.isoweekday() not in {1, 2, 3, 4, 5}:
        dt += timedelta(days=1)
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0)


def test_create_appointment_success():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday())
    assert appt.status == AppointmentStatus.PENDING
    assert appt.is_active is True


def test_create_appointment_in_past_raises():
    past = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(AppointmentInThePastException):
        Appointment.create(uuid4(), uuid4(), past)


def test_create_appointment_on_weekend_raises():
    dt = datetime.now(timezone.utc) + timedelta(days=1)
    while dt.isoweekday() not in {6, 7}:
        dt += timedelta(days=1)
    dt = dt.replace(hour=10, minute=0, second=0, microsecond=0)
    with pytest.raises(AppointmentOutsideWorkingHoursException):
        Appointment.create(uuid4(), uuid4(), dt)


def test_create_appointment_outside_hours_raises():
    with pytest.raises(AppointmentOutsideWorkingHoursException):
        Appointment.create(uuid4(), uuid4(), future_weekday(hour=7))

    with pytest.raises(AppointmentOutsideWorkingHoursException):
        Appointment.create(uuid4(), uuid4(), future_weekday(hour=17))


def test_create_appointment_without_timezone_raises():
    naive = datetime.now() + timedelta(days=1)
    with pytest.raises(ValueError):
        Appointment.create(uuid4(), uuid4(), naive)


def test_confirm_appointment():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday())
    appt.confirm()
    assert appt.status == AppointmentStatus.CONFIRMED
    assert appt.is_active is True


def test_cancel_appointment():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday())
    appt.cancel()
    assert appt.status == AppointmentStatus.CANCELLED
    assert appt.is_active is False


def test_complete_appointment():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday())
    appt.confirm()
    appt.complete()
    assert appt.status == AppointmentStatus.COMPLETED
    assert appt.is_active is False


def test_mark_no_show():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday())
    appt.confirm()
    appt.mark_no_show()
    assert appt.status == AppointmentStatus.NO_SHOW


def test_invalid_transition_raises():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday())
    appt.cancel()
    with pytest.raises(InvalidStatusTransitionException):
        appt.confirm()


def test_appointment_with_notes():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday(), notes="Consulta general")
    assert appt.notes == "Consulta general"


def test_appointment_custom_duration():
    appt = Appointment.create(uuid4(), uuid4(), future_weekday(), duration_minutes=60)
    assert appt.duration_minutes == 60