from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.http.dependencies import get_current_user, require_admin
from app.adapters.http.schemas.patient_schema import (
    PatientResponse,
    RegisterPatientRequest,
)
from app.application.dtos.patient_dto import RegisterPatientDTO
from app.application.use_cases.patient.get_patient import (
    GetPatientByIdUseCase,
    GetPatientsUseCase,
)
from app.application.use_cases.patient.register_patient import RegisterPatientUseCase
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.patient_repository_impl import (
    PatientRepositoryImpl,
)
from app.infrastructure.persistence.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.infrastructure.security.password_hasher import PasswordHasher

router = APIRouter(prefix="/patients", tags=["patients"])


# ── Factories ──────────────────────────────────────────────────────────────────

def _register_uc(session: AsyncSession) -> RegisterPatientUseCase:
    return RegisterPatientUseCase(
        user_repository=UserRepositoryImpl(session),
        patient_repository=PatientRepositoryImpl(session),
        password_hasher=PasswordHasher(),
    )


def _get_by_id_uc(session: AsyncSession) -> GetPatientByIdUseCase:
    return GetPatientByIdUseCase(PatientRepositoryImpl(session))


def _get_all_uc(session: AsyncSession) -> GetPatientsUseCase:
    return GetPatientsUseCase(PatientRepositoryImpl(session))


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=PatientResponse,
    status_code=201,
    summary="Registrar paciente nuevo",
)
async def register_patient(
    body: RegisterPatientRequest,
    session: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    dto = RegisterPatientDTO(
        email=body.email,
        password=body.password,
        first_name=body.first_name,
        last_name=body.last_name,
        birth_date=body.birth_date,
        phone=body.phone,
        document_number=body.document_number,
        document_type=body.document_type,
        gender=body.gender,
        address=body.address,
    )
    result = await _register_uc(session).execute(dto)
    return PatientResponse(**result.__dict__)


@router.get(
    "",
    response_model=list[PatientResponse],
    summary="Listar pacientes (admin)",
    dependencies=[Depends(require_admin)],
)
async def get_patients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[PatientResponse]:
    results = await _get_all_uc(session).execute(skip=skip, limit=limit)
    return [PatientResponse(**r.__dict__) for r in results]


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Obtener paciente por ID",
)
async def get_patient(
    patient_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _current_user=Depends(get_current_user),
) -> PatientResponse:
    result = await _get_by_id_uc(session).execute(patient_id)
    return PatientResponse(**result.__dict__)