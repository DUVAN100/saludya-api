from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.output.i_patient_repository import IPatientRepository
from app.domain.entities.patient import Patient
from app.infrastructure.persistence.models.patient_model import PatientModel


class PatientRepositoryImpl(IPatientRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, patient: Patient) -> Patient:
        model = _to_model(patient)
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def find_by_id(self, patient_id: UUID) -> Patient | None:
        result = await self._session.execute(
            select(PatientModel).where(PatientModel.id == patient_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_user_id(self, user_id: UUID) -> Patient | None:
        result = await self._session.execute(
            select(PatientModel).where(PatientModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_document_number(self, document_number: str) -> Patient | None:
        result = await self._session.execute(
            select(PatientModel).where(
                PatientModel.document_number == document_number
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_all(self, skip: int = 0, limit: int = 20) -> list[Patient]:
        result = await self._session.execute(
            select(PatientModel)
            .order_by(PatientModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def update(self, patient: Patient) -> Patient:
        result = await self._session.execute(
            select(PatientModel).where(PatientModel.id == patient.id)
        )
        model = result.scalar_one()
        model.first_name = patient.first_name
        model.last_name = patient.last_name
        model.birth_date = patient.birth_date
        model.phone = patient.phone
        model.document_number = patient.document_number
        model.document_type = patient.document_type
        model.gender = patient.gender
        model.address = patient.address
        await self._session.flush()
        return _to_entity(model)

    async def exists_by_document_number(self, document_number: str) -> bool:
        result = await self._session.execute(
            select(PatientModel.id).where(
                PatientModel.document_number == document_number
            )
        )
        return result.scalar_one_or_none() is not None


# ── Mappers ───────────────────────────────────────────────────────────────────

def _to_model(patient: Patient) -> PatientModel:
    return PatientModel(
        id=patient.id,
        user_id=patient.user_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        birth_date=patient.birth_date,
        phone=patient.phone,
        document_number=patient.document_number,
        document_type=patient.document_type,
        gender=patient.gender,
        address=patient.address,
        created_at=patient.created_at,
    )


def _to_entity(model: PatientModel) -> Patient:
    return Patient(
        id=model.id,
        user_id=model.user_id,
        first_name=model.first_name,
        last_name=model.last_name,
        birth_date=model.birth_date,
        phone=model.phone,
        document_number=model.document_number,
        document_type=model.document_type,
        gender=model.gender,
        address=model.address,
        created_at=model.created_at,
    )