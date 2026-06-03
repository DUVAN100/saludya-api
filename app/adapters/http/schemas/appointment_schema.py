from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.domain.value_objects.appointment_status import AppointmentStatus


class CreateAppointmentRequest(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime = Field(
        description="Fecha y hora de la cita (timezone-aware, lun-vie 08:00-17:00)"
    )
    duration_minutes: int = Field(default=30, ge=10, le=120)
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def scheduled_at_must_be_timezone_aware(self) -> "CreateAppointmentRequest":
        if self.scheduled_at.tzinfo is None:
            raise ValueError("scheduled_at debe incluir zona horaria (ej: 2025-06-10T10:00:00-05:00)")
        return self

    model_config = {"json_schema_extra": {"example": {
        "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "doctor_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "scheduled_at": "2025-06-10T10:00:00-05:00",
        "duration_minutes": 30,
        "notes": "Primera consulta",
    }}}


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    status: AppointmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int