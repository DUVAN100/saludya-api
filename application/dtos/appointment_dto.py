from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.appointment_status import AppointmentStatus


@dataclass(frozen=True)
class AppointmentDTO:
    """DTO de salida — representa una cita ya persistida."""
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    status: AppointmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateAppointmentDTO:
    """DTO de entrada — datos para agendar una cita."""
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    duration_minutes: int = 30
    notes: str | None = None


@dataclass(frozen=True)
class CancelAppointmentDTO:
    """DTO de entrada — identifica la cita a cancelar."""
    appointment_id: UUID


@dataclass(frozen=True)
class ConfirmAppointmentDTO:
    """DTO de entrada — identifica la cita a confirmar."""
    appointment_id: UUID