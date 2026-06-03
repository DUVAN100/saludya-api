from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.http.dependencies import get_current_user, require_admin
from app.adapters.http.schemas.doctor_schema import CreateDoctorRequest, DoctorResponse
from app.application.dtos.doctor_dto import CreateDoctorDTO
from app.application.use_cases.doctor.create_doctor import CreateDoctorUseCase
from app.application.use_cases.doctor.get_doctor import (
    GetDoctorByIdUseCase,
    GetDoctorsUseCase,
)
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.doctor_repository_impl import (
    DoctorRepositoryImpl,
)
from app.infrastructure.persistence.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.infrastructure.security.password_hasher import PasswordHasher

router = APIRouter(prefix="/doctors", tags=["doctors"])


# ── Factories ──────────────────────────────────────────────────────────────────

def _create_uc(session: AsyncSession) -> CreateDoctorUseCase:
    return CreateDoctorUseCase(
        user_repository=UserRepositoryImpl(session),
        doctor_repository=DoctorRepositoryImpl(session),
        password_hasher=PasswordHasher(),
    )


def _get_by_id_uc(session: AsyncSession) -> GetDoctorByIdUseCase:
    return GetDoctorByIdUseCase(DoctorRepositoryImpl(session))


def _get_all_uc(session: AsyncSession) -> GetDoctorsUseCase:
    return GetDoctorsUseCase(DoctorRepositoryImpl(session))


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=DoctorResponse,
    status_code=201,
    summary="Crear médico (admin)",
    dependencies=[Depends(require_admin)],
)
async def create_doctor(
    body: CreateDoctorRequest,
    session: AsyncSession = Depends(get_db_session),
) -> DoctorResponse:
    dto = CreateDoctorDTO(
        email=body.email,
        password=body.password,
        first_name=body.first_name,
        last_name=body.last_name,
        specialty=body.specialty,
        license_number=body.license_number,
        phone=body.phone,
        consultation_duration=body.consultation_duration,
    )
    result = await _create_uc(session).execute(dto)
    return _to_response(result)


@router.get(
    "",
    response_model=list[DoctorResponse],
    summary="Listar médicos",
)
async def get_doctors(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> list[DoctorResponse]:
    results = await _get_all_uc(session).execute(skip=skip, limit=limit)
    return [_to_response(r) for r in results]


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Obtener médico por ID",
)
async def get_doctor(
    doctor_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> DoctorResponse:
    result = await _get_by_id_uc(session).execute(doctor_id)
    return _to_response(result)


# ── Mapper ─────────────────────────────────────────────────────────────────────

def _to_response(dto) -> DoctorResponse:
    from app.adapters.http.schemas.doctor_schema import DoctorAvailabilityResponse
    return DoctorResponse(
        id=dto.id,
        user_id=dto.user_id,
        first_name=dto.first_name,
        last_name=dto.last_name,
        full_name=dto.full_name,
        specialty=dto.specialty,
        license_number=dto.license_number,
        phone=dto.phone,
        consultation_duration=dto.consultation_duration,
        availability=[
            DoctorAvailabilityResponse(
                id=a.id,
                day_of_week=a.day_of_week,
                start_time=a.start_time,
                end_time=a.end_time,
                is_active=a.is_active,
            )
            for a in dto.availability
        ],
        created_at=dto.created_at,
    )