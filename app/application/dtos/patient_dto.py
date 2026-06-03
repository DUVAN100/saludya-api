from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class PatientDTO:
    """DTO de salida — representa un paciente ya persistido."""
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    full_name: str
    birth_date: date | None
    age: int | None
    phone: str | None
    document_number: str | None
    document_type: str | None
    gender: str | None
    address: str | None
    created_at: datetime


@dataclass(frozen=True)
class RegisterPatientDTO:
    """DTO de entrada — datos para registrar un paciente nuevo."""
    email: str
    password: str
    first_name: str
    last_name: str
    birth_date: date | None = None
    phone: str | None = None
    document_number: str | None = None
    document_type: str | None = None
    gender: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class UpdatePatientDTO:
    """DTO de entrada — campos opcionales para actualizar un paciente."""
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    gender: str | None = None