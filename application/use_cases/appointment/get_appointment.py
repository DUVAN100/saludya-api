from uuid import UUID

from app.application.dtos.appointment_dto import AppointmentDTO
from app.application.ports.output.i_appointment_repository import IAppointmentRepository
from app.domain.entities.appointment import Appointment
from app.domain.exceptions.domain_exceptions import AppointmentNotFoundException
from app.domain.value_objects.appointment_status import AppointmentStatus


class GetAppointmentByIdUseCase:
    def __init__(self, appointment_repository: IAppointmentRepository) -> None:
        self._repo = appointment_repository

    async def execute(self, appointment_id: UUID) -> AppointmentDTO:
        appointment = await self._repo.find_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(str(appointment_id))
        return _to_dto(appointment)


class GetAppointmentsByPatientUseCase:
    def __init__(self, appointment_repository: IAppointmentRepository) -> None:
        self._repo = appointment_repository

    async def execute(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentDTO]:
        appointments = await self._repo.find_by_patient_id(
            patient_id, skip=skip, limit=limit
        )
        return [_to_dto(a) for a in appointments]


class GetAppointmentsByDoctorUseCase:
    def __init__(self, appointment_repository: IAppointmentRepository) -> None:
        self._repo = appointment_repository

    async def execute(
        self,
        doctor_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentDTO]:
        appointments = await self._repo.find_by_doctor_id(
            doctor_id, skip=skip, limit=limit
        )
        return [_to_dto(a) for a in appointments]


class GetAllAppointmentsUseCase:
    """Para el panel administrativo."""

    def __init__(self, appointment_repository: IAppointmentRepository) -> None:
        self._repo = appointment_repository

    async def execute(
        self,
        status: AppointmentStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentDTO]:
        appointments = await self._repo.find_all(
            status=status, skip=skip, limit=limit
        )
        return [_to_dto(a) for a in appointments]


def _to_dto(appointment: Appointment) -> AppointmentDTO:
    return AppointmentDTO(
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