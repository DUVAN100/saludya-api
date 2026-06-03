from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class DoctorAvailabilityResponse(BaseModel):
    id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool

    model_config = {"from_attributes": True}


class CreateDoctorRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=1, max_length=100)
    license_number: str = Field(min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    consultation_duration: int = Field(default=30, ge=10, le=120)

    model_config = {"json_schema_extra": {"example": {
        "email": "dr.carlos@clinic.com",
        "password": "secret123",
        "first_name": "Carlos",
        "last_name": "Pérez",
        "specialty": "Cardiología",
        "license_number": "MED-001",
        "consultation_duration": 30,
    }}}


class UpdateDoctorRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    specialty: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    consultation_duration: int | None = Field(default=None, ge=10, le=120)


class DoctorResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    full_name: str
    specialty: str
    license_number: str
    phone: str | None
    consultation_duration: int
    availability: list[DoctorAvailabilityResponse]
    created_at: datetime

    model_config = {"from_attributes": True}