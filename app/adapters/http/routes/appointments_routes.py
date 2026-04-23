from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.http.dependencies import get_current_user, require_admin_or_doctor
from app.adapters.http.schemas.appointment_schema import (
    AppointmentListResponse,
    AppointmentResponse,
    CreateAppointmentRequest,
)
from app.application.dtos.appointment_dto import CreateAppointmentDTO
from app.application.use_cases.appointment.create_appointment import (
    CreateAppointmentUseCase,
)
from app.application.use_cases.appointment.get_appointment import (
    GetAllAppointmentsUseCase,
    GetAppointmentByIdUseCase,
    GetAppointmentsByDoctorUseCase,
    GetAppointmentsByPatientUseCase,
)
from app.application.use_cases.appointment.update_appointment_status import (
    CancelAppointmentUseCase,
    ConfirmAppointmentUseCase,
)
from app.domain.value_objects.appointment_status import AppointmentStatus
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.appointment_repository_impl import (
    AppointmentRepositoryImpl,
)
from app.infrastructure.persistence.repositories.doctor_repository_impl import (
    DoctorRepositoryImpl,
)
from app.infrastructure.persistence.repositories.patient_repository_impl import (
    PatientRepositoryImpl,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


# ── Factories ──────────────────────────────────────────────────────────────────

def _create_uc(session: AsyncSession) -> CreateAppointmentUseCase:
    return CreateAppointmentUseCase(
        appointment_repository=AppointmentRepositoryImpl(session),
        doctor_repository=DoctorRepositoryImpl(session),
        patient_repository=PatientRepositoryImpl(session),
    )


def _confirm_uc(session: AsyncSession) -> ConfirmAppointmentUseCase:
    return ConfirmAppointmentUseCase(AppointmentRepositoryImpl(session))


def _cancel_uc(session: AsyncSession) -> CancelAppointmentUseCase:
    return CancelAppointmentUseCase(AppointmentRepositoryImpl(session))


def _get_by_id_uc(session: AsyncSession) -> GetAppointmentByIdUseCase:
    return GetAppointmentByIdUseCase(AppointmentRepositoryImpl(session))


def _get_by_patient_uc(session: AsyncSession) -> GetAppointmentsByPatientUseCase:
    return GetAppointmentsByPatientUseCase(AppointmentRepositoryImpl(session))


def _get_by_doctor_uc(session: AsyncSession) -> GetAppointmentsByDoctorUseCase:
    return GetAppointmentsByDoctorUseCase(AppointmentRepositoryImpl(session))


def _get_all_uc(session: AsyncSession) -> GetAllAppointmentsUseCase:
    return GetAllAppointmentsUseCase(AppointmentRepositoryImpl(session))


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=201,
    summary="Agendar una cita",
)
async def create_appointment(
    body: CreateAppointmentRequest,
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> AppointmentResponse:
    dto = CreateAppointmentDTO(
        patient_id=body.patient_id,
        doctor_id=body.doctor_id,
        scheduled_at=body.scheduled_at,
        duration_minutes=body.duration_minutes,
        notes=body.notes,
    )
    result = await _create_uc(session).execute(dto)
    return AppointmentResponse(**result.__dict__)


@router.patch(
    "/{appointment_id}/confirm",
    response_model=AppointmentResponse,
    summary="Confirmar cita (médico o admin)",
    dependencies=[Depends(require_admin_or_doctor)],
)
async def confirm_appointment(
    appointment_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    result = await _confirm_uc(session).execute(appointment_id)
    return AppointmentResponse(**result.__dict__)


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    summary="Cancelar una cita",
)
async def cancel_appointment(
    appointment_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> AppointmentResponse:
    result = await _cancel_uc(session).execute(appointment_id)
    return AppointmentResponse(**result.__dict__)


@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse],
    summary="Citas de un paciente",
)
async def get_appointments_by_patient(
    patient_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> list[AppointmentResponse]:
    results = await _get_by_patient_uc(session).execute(
        patient_id, skip=skip, limit=limit
    )
    return [AppointmentResponse(**r.__dict__) for r in results]


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[AppointmentResponse],
    summary="Agenda de un médico",
    dependencies=[Depends(require_admin_or_doctor)],
)
async def get_appointments_by_doctor(
    doctor_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[AppointmentResponse]:
    results = await _get_by_doctor_uc(session).execute(
        doctor_id, skip=skip, limit=limit
    )
    return [AppointmentResponse(**r.__dict__) for r in results]


@router.get(
    "",
    response_model=AppointmentListResponse,
    summary="Listar todas las citas (admin)",
    dependencies=[Depends(require_admin_or_doctor)],
)
async def get_all_appointments(
    status: AppointmentStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentListResponse:
    results = await _get_all_uc(session).execute(status=status, skip=skip, limit=limit)
    return AppointmentListResponse(
        items=[AppointmentResponse(**r.__dict__) for r in results],
        total=len(results),
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Obtener cita por ID",
)
async def get_appointment(
    appointment_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> AppointmentResponse:
    result = await _get_by_id_uc(session).execute(appointment_id)
    return AppointmentResponse(**result.__dict__)