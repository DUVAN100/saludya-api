class DomainException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


# ── User ──────────────────────────────────────────────────────────────────────

class UserNotFoundException(DomainException):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"User not found: '{identifier}'")


class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' already exists")


class InvalidCredentialsException(DomainException):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveUserException(DomainException):
    def __init__(self) -> None:
        super().__init__("This account is inactive")


# ── Patient ───────────────────────────────────────────────────────────────────

class PatientNotFoundException(DomainException):
    def __init__(self, patient_id: str) -> None:
        super().__init__(f"Patient not found: '{patient_id}'")


class PatientAlreadyExistsException(DomainException):
    def __init__(self, document_number: str) -> None:
        super().__init__(
            f"A patient with document number '{document_number}' already exists"
        )


# ── Doctor ────────────────────────────────────────────────────────────────────

class DoctorNotFoundException(DomainException):
    def __init__(self, doctor_id: str) -> None:
        super().__init__(f"Doctor not found: '{doctor_id}'")


class DoctorNotAvailableException(DomainException):
    def __init__(self, doctor_id: str, scheduled_at: str) -> None:
        super().__init__(
            f"Doctor '{doctor_id}' is not available at '{scheduled_at}'"
        )


# ── Appointment ───────────────────────────────────────────────────────────────

class AppointmentNotFoundException(DomainException):
    def __init__(self, appointment_id: str) -> None:
        super().__init__(f"Appointment not found: '{appointment_id}'")


class AppointmentSlotTakenException(DomainException):
    def __init__(self, doctor_id: str, scheduled_at: str) -> None:
        super().__init__(
            f"The slot '{scheduled_at}' is already taken for doctor '{doctor_id}'"
        )


class InvalidStatusTransitionException(DomainException):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            f"Cannot transition appointment from '{current}' to '{target}'"
        )


class AppointmentOutsideWorkingHoursException(DomainException):
    def __init__(self, scheduled_at: str) -> None:
        super().__init__(
            f"Appointment at '{scheduled_at}' is outside working hours (Mon–Fri 08:00–17:00)"
        )


class AppointmentInThePastException(DomainException):
    def __init__(self) -> None:
        super().__init__("Cannot schedule an appointment in the past")