from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.ports.output.i_doctor_repository import IDoctorRepository
from app.domain.entities.doctor import Doctor, DoctorAvailability
from app.infrastructure.persistence.models.doctor_model import (
    DoctorAvailabilityModel,
    DoctorModel,
)


class DoctorRepositoryImpl(IDoctorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, doctor: Doctor) -> Doctor:
        model = DoctorModel(
            id=doctor.id,
            user_id=doctor.user_id,
            first_name=doctor.first_name,
            last_name=doctor.last_name,
            specialty=doctor.specialty,
            license_number=doctor.license_number,
            phone=doctor.phone,
            consultation_duration=doctor.consultation_duration,
            created_at=doctor.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return doctor

    async def find_by_id(self, doctor_id: UUID) -> Doctor | None:
        result = await self._session.execute(
            select(DoctorModel).where(DoctorModel.id == doctor_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_id_with_availability(self, doctor_id: UUID) -> Doctor | None:
        result = await self._session.execute(
            select(DoctorModel)
            .options(selectinload(DoctorModel.availability))
            .where(DoctorModel.id == doctor_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        doctor = _to_entity(model)
        doctor.availability = [_avail_to_entity(a) for a in model.availability]
        return doctor

    async def find_by_user_id(self, user_id: UUID) -> Doctor | None:
        result = await self._session.execute(
            select(DoctorModel).where(DoctorModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_all(self, skip: int = 0, limit: int = 20) -> list[Doctor]:
        result = await self._session.execute(
            select(DoctorModel)
            .options(selectinload(DoctorModel.availability))
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        doctors = []
        for m in models:
            d = _to_entity(m)
            d.availability = [_avail_to_entity(a) for a in m.availability]
            doctors.append(d)
        return doctors

    async def find_by_specialty(self, specialty: str) -> list[Doctor]:
        result = await self._session.execute(
            select(DoctorModel).where(DoctorModel.specialty == specialty)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def update(self, doctor: Doctor) -> Doctor:
        result = await self._session.execute(
            select(DoctorModel).where(DoctorModel.id == doctor.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.first_name = doctor.first_name
            model.last_name = doctor.last_name
            model.specialty = doctor.specialty
            model.phone = doctor.phone
            model.consultation_duration = doctor.consultation_duration
            await self._session.flush()
        return doctor

    async def exists_by_license_number(self, license_number: str) -> bool:
        result = await self._session.execute(
            select(DoctorModel.id).where(
                DoctorModel.license_number == license_number
            )
        )
        return result.scalar_one_or_none() is not None

    async def save_availability(
        self, availability: DoctorAvailability
    ) -> DoctorAvailability:
        model = DoctorAvailabilityModel(
            id=availability.id,
            doctor_id=availability.doctor_id,
            day_of_week=availability.day_of_week,
            start_time=availability.start_time,
            end_time=availability.end_time,
            is_active=availability.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return availability


def _to_entity(model: DoctorModel) -> Doctor:
    return Doctor(
        id=model.id,
        user_id=model.user_id,
        first_name=model.first_name,
        last_name=model.last_name,
        specialty=model.specialty,
        license_number=model.license_number,
        phone=model.phone,
        consultation_duration=model.consultation_duration,
        created_at=model.created_at,
    )


def _avail_to_entity(model: DoctorAvailabilityModel) -> DoctorAvailability:
    return DoctorAvailability(
        id=model.id,
        doctor_id=model.doctor_id,
        day_of_week=model.day_of_week,
        start_time=model.start_time,
        end_time=model.end_time,
        is_active=model.is_active,
    )