from uuid import UUID

from app.application.dtos.appointment_dto import AppointmentDTO
from app.application.ports.output.i_appointment_repository import IAppointmentRepository
from app.domain.entities.appointment import Appointment
from app.domain.exceptions.domain_exceptions import AppointmentNotFoundException


class ConfirmAppointmentUseCase:
    """Caso de uso: confirmar una cita pendiente."""

    def __init__(self, appointment_repository: IAppointmentRepository) -> None:
        self._repo = appointment_repository

    async def execute(self, appointment_id: UUID) -> AppointmentDTO:
        appointment = await self._get_or_raise(appointment_id)
        appointment.confirm()                          # lógica en la entidad
        saved = await self._repo.update(appointment)
        return _to_dto(saved)

    async def _get_or_raise(self, appointment_id: UUID) -> Appointment:
        appointment = await self._repo.find_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(str(appointment_id))
        return appointment


class CancelAppointmentUseCase:
    """Caso de uso: cancelar una cita pendiente o confirmada."""

    def __init__(self, appointment_repository: IAppointmentRepository) -> None:
        self._repo = appointment_repository

    async def execute(self, appointment_id: UUID) -> AppointmentDTO:
        appointment = await self._repo.find_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(str(appointment_id))
        appointment.cancel()                           # valida transición en la entidad
        saved = await self._repo.update(appointment)
        return _to_dto(saved)


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