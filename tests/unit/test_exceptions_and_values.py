import pytest
from app.domain.exceptions.domain_exceptions import (
    DomainException,
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InactiveUserException,
    PatientNotFoundException,
    PatientAlreadyExistsException,
    DoctorNotFoundException,
    DoctorNotAvailableException,
    AppointmentNotFoundException,
    AppointmentSlotTakenException,
    InvalidStatusTransitionException,
    AppointmentOutsideWorkingHoursException,
    AppointmentInThePastException,
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole
from app.domain.entities.user import User


# ── Exceptions ────────────────────────────────────────────────

def test_domain_exception_message():
    exc = DomainException("error base")
    assert exc.message == "error base"
    assert str(exc) == "error base"


def test_user_not_found_exception():
    exc = UserNotFoundException("abc-123")
    assert "abc-123" in exc.message


def test_user_already_exists_exception():
    exc = UserAlreadyExistsException("test@example.com")
    assert "test@example.com" in exc.message


def test_invalid_credentials_exception():
    exc = InvalidCredentialsException()
    assert "Invalid" in exc.message


def test_inactive_user_exception():
    exc = InactiveUserException()
    assert "inactive" in exc.message


def test_patient_not_found_exception():
    exc = PatientNotFoundException("pat-001")
    assert "pat-001" in exc.message


def test_patient_already_exists_exception():
    exc = PatientAlreadyExistsException("DOC-001")
    assert "DOC-001" in exc.message


def test_doctor_not_found_exception():
    exc = DoctorNotFoundException("doc-001")
    assert "doc-001" in exc.message


def test_doctor_not_available_exception():
    exc = DoctorNotAvailableException("doc-001", "2026-06-10 10:00")
    assert "doc-001" in exc.message
    assert "2026-06-10" in exc.message


def test_appointment_not_found_exception():
    exc = AppointmentNotFoundException("appt-001")
    assert "appt-001" in exc.message


def test_appointment_slot_taken_exception():
    exc = AppointmentSlotTakenException("doc-001", "2026-06-10 10:00")
    assert "doc-001" in exc.message


def test_invalid_status_transition_exception():
    exc = InvalidStatusTransitionException("pending", "completed")
    assert "pending" in exc.message
    assert "completed" in exc.message


def test_appointment_outside_working_hours_exception():
    exc = AppointmentOutsideWorkingHoursException("2026-06-10 18:00")
    assert "2026-06-10" in exc.message


def test_appointment_in_the_past_exception():
    exc = AppointmentInThePastException()
    assert "past" in exc.message


# ── Email value object ────────────────────────────────────────

def test_email_valid():
    email = Email("user@example.com")
    assert email.value == "user@example.com"
    assert str(email) == "user@example.com"


@pytest.mark.parametrize("value", [
    "",
    "invalid",
    "missing-at.com",
    "a@b",
    "@example.com",
    "user@.com",
])
def test_email_invalid(value):
    with pytest.raises(ValueError):
        Email(value)


# ── UserRole value object ─────────────────────────────────────

def test_user_role_values():
    assert UserRole.admin.value == "admin"
    assert UserRole.doctor.value == "doctor"
    assert UserRole.patient.value == "patient"


def test_user_role_from_string():
    assert UserRole("admin") == UserRole.admin
    assert UserRole("doctor") == UserRole.doctor
    assert UserRole("patient") == UserRole.patient


# ── User entity ───────────────────────────────────────────────

def test_user_is_active_by_default():
    user = User(
        email=Email("user@example.com"),
        password_hash="hash",
        role=UserRole.patient,
    )
    assert user.is_active is True
    assert user.is_patient() is True
    assert user.is_doctor() is False
    assert user.is_admin() is False


def test_user_deactivate_and_activate():
    user = User(
        email=Email("user@example.com"),
        password_hash="hash",
        role=UserRole.doctor,
    )
    user.deactivate()
    assert user.is_active is False

    user.activate()
    assert user.is_active is True


def test_user_role_helpers():
    admin = User(email=Email("admin@example.com"), password_hash="h", role=UserRole.admin)
    doctor = User(email=Email("doctor@example.com"), password_hash="h", role=UserRole.doctor)
    patient = User(email=Email("patient@example.com"), password_hash="h", role=UserRole.patient)

    assert admin.is_admin() is True
    assert admin.is_doctor() is False
    assert doctor.is_doctor() is True
    assert doctor.is_patient() is False
    assert patient.is_patient() is True
    assert patient.is_admin() is False


def test_user_touch_updates_updated_at():
    user = User(
        email=Email("user@example.com"),
        password_hash="hash",
        role=UserRole.patient,
    )
    original = user.updated_at
    user.deactivate()
    assert user.updated_at >= original