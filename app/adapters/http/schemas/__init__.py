from .auth_schema import LoginRequest, TokenResponse
from .user_schema import UserResponse
from .patient_schema import RegisterPatientRequest, UpdatePatientRequest, PatientResponse
from .doctor_schema import (
    CreateDoctorRequest,
    UpdateDoctorRequest,
    DoctorResponse,
    DoctorAvailabilityResponse,
)
from .appointment_schema import (
    CreateAppointmentRequest,
    AppointmentResponse,
    AppointmentListResponse,
)

__all__ = [
    "LoginRequest", "TokenResponse",
    "UserResponse",
    "RegisterPatientRequest", "UpdatePatientRequest", "PatientResponse",
    "CreateDoctorRequest", "UpdateDoctorRequest", "DoctorResponse", "DoctorAvailabilityResponse",
    "CreateAppointmentRequest", "AppointmentResponse", "AppointmentListResponse",
]