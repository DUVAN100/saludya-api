from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.value_objects.appointment_status import AppointmentStatus
from app.domain.exceptions.domain_exceptions import (
    InvalidStatusTransitionException,
    AppointmentInThePastException,
    AppointmentOutsideWorkingHoursException,
)

_WORKING_HOUR_START = 8
_WORKING_HOUR_END = 17
_WORKING_DAYS = frozenset({1, 2, 3, 4, 5})   # Mon–Fri (isoweekday)


@dataclass
class Appointment:
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    id: UUID = field(default_factory=uuid4)
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.PENDING
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Factories ─────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        patient_id: UUID,
        doctor_id: UUID,
        scheduled_at: datetime,
        duration_minutes: int = 30,
        notes: str | None = None,
    ) -> "Appointment":
        cls._validate_scheduled_at(scheduled_at)
        return cls(
            patient_id=patient_id,
            doctor_id=doctor_id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            notes=notes,
        )

    # ── Commands ──────────────────────────────────────────────────────────────

    def confirm(self) -> None:
        self._transition_to(AppointmentStatus.CONFIRMED)

    def cancel(self) -> None:
        self._transition_to(AppointmentStatus.CANCELLED)

    def complete(self) -> None:
        self._transition_to(AppointmentStatus.COMPLETED)

    def mark_no_show(self) -> None:
        self._transition_to(AppointmentStatus.NO_SHOW)

    # ── Queries ───────────────────────────────────────────────────────────────

    @property
    def is_active(self) -> bool:
        return self.status in {
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _transition_to(self, new_status: AppointmentStatus) -> None:
        if not self.status.can_transition_to(new_status):
            raise InvalidStatusTransitionException(
                self.status.value, new_status.value
            )
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def _validate_scheduled_at(scheduled_at: datetime) -> None:
        now = datetime.now(timezone.utc)

        if scheduled_at.tzinfo is None:
            raise ValueError("scheduled_at must be timezone-aware")

        if scheduled_at <= now:
            raise AppointmentInThePastException()

        if scheduled_at.isoweekday() not in _WORKING_DAYS:
            raise AppointmentOutsideWorkingHoursException(str(scheduled_at))

        if not (_WORKING_HOUR_START <= scheduled_at.hour < _WORKING_HOUR_END):
            raise AppointmentOutsideWorkingHoursException(str(scheduled_at))