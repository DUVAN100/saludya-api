from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterPatientRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    birth_date: date | None = None
    phone: str | None = Field(default=None, max_length=20)
    document_number: str | None = Field(default=None, max_length=30)
    document_type: str | None = Field(default=None, pattern="^(CC|CE|TI|PP)$")
    gender: str | None = Field(default=None, pattern="^(M|F|otro)$")
    address: str | None = None

    model_config = {"json_schema_extra": {"example": {
        "email": "juan@email.com",
        "password": "secret123",
        "first_name": "Juan",
        "last_name": "García",
        "birth_date": "1990-05-15",
        "document_number": "12345678",
        "document_type": "CC",
    }}}


class UpdatePatientRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = None
    gender: str | None = Field(default=None, pattern="^(M|F|otro)$")


class PatientResponse(BaseModel):
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

    model_config = {"from_attributes": True}