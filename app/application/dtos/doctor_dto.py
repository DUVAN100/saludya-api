from dataclasses import dataclass
from datetime import datetime, time
from uuid import UUID


@dataclass(frozen=True)
class DoctorAvailabilityDTO:
    id: UUID
    day_of_week: int       # 1 = lunes … 5 = viernes
    start_time: time
    end_time: time
    is_active: bool


@dataclass(frozen=True)
class DoctorDTO:
    """DTO de salida — representa un médico ya persistido."""
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    full_name: str
    specialty: str
    license_number: str
    phone: str | None
    consultation_duration: int
    availability: list[DoctorAvailabilityDTO]
    created_at: datetime


@dataclass(frozen=True)
class CreateDoctorDTO:
    """DTO de entrada — datos para crear un médico nuevo."""
    email: str
    password: str
    first_name: str
    last_name: str
    specialty: str
    license_number: str
    phone: str | None = None
    consultation_duration: int = 30


@dataclass(frozen=True)
class UpdateDoctorDTO:
    """DTO de entrada — campos opcionales para actualizar un médico."""
    first_name: str | None = None
    last_name: str | None = None
    specialty: str | None = None
    phone: str | None = None
    consultation_duration: int | None = None