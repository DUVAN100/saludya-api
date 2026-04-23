from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.output.i_appointment_repository import IAppointmentRepository
from app.domain.entities.appointment import Appointment
from app.domain.value_objects.appointment_status import AppointmentStatus
from app.infrastructure.persistence.models.appointment_model import AppointmentModel


class AppointmentRepositoryImpl(IAppointmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, appointment: Appointment) -> Appointment:
        model = AppointmentModel(
            id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            scheduled_at=appointment.scheduled_at,
            duration_minutes=appointment.duration_minutes,
            status=appointment.status,
            notes=appointment.notes,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return appointment

    async def find_by_id(self, appointment_id: UUID) -> Appointment | None:
        result = await self._session.execute(
            select(AppointmentModel).where(AppointmentModel.id == appointment_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_patient_id(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel)
            .where(AppointmentModel.patient_id == patient_id)
            .order_by(AppointmentModel.scheduled_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def find_by_doctor_id(
        self,
        doctor_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel)
            .where(AppointmentModel.doctor_id == doctor_id)
            .order_by(AppointmentModel.scheduled_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def find_by_doctor_and_date_range(
        self,
        doctor_id: UUID,
        start: datetime,
        end: datetime,
    ) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel).where(
                and_(
                    AppointmentModel.doctor_id == doctor_id,
                    AppointmentModel.scheduled_at >= start,
                    AppointmentModel.scheduled_at <= end,
                )
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def exists_slot_taken(
        self,
        doctor_id: UUID,
        scheduled_at: datetime,
        exclude_appointment_id: UUID | None = None,
    ) -> bool:
        conditions = [
            AppointmentModel.doctor_id == doctor_id,
            AppointmentModel.scheduled_at == scheduled_at,
            AppointmentModel.status.in_(
                [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
            ),
        ]
        if exclude_appointment_id:
            conditions.append(AppointmentModel.id != exclude_appointment_id)

        result = await self._session.execute(
            select(AppointmentModel.id).where(and_(*conditions))
        )
        return result.scalar_one_or_none() is not None

    async def update(self, appointment: Appointment) -> Appointment:
        result = await self._session.execute(
            select(AppointmentModel).where(AppointmentModel.id == appointment.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = appointment.status
            model.notes = appointment.notes
            model.updated_at = appointment.updated_at
            await self._session.flush()
        return appointment

    async def find_all(
        self,
        status: AppointmentStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        query = select(AppointmentModel).order_by(
            AppointmentModel.scheduled_at.desc()
        )
        if status:
            query = query.where(AppointmentModel.status == status)
        result = await self._session.execute(query.offset(skip).limit(limit))
        return [_to_entity(m) for m in result.scalars().all()]


def _to_entity(model: AppointmentModel) -> Appointment:
    return Appointment(
        id=model.id,
        patient_id=model.patient_id,
        doctor_id=model.doctor_id,
        scheduled_at=model.scheduled_at,
        duration_minutes=model.duration_minutes,
        status=model.status,
        notes=model.notes,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )