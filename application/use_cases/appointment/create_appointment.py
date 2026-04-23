from app.application.dtos.appointment_dto import AppointmentDTO, CreateAppointmentDTO
from app.application.ports.output.i_appointment_repository import IAppointmentRepository
from app.application.ports.output.i_doctor_repository import IDoctorRepository
from app.application.ports.output.i_patient_repository import IPatientRepository
from app.domain.entities.appointment import Appointment
from app.domain.exceptions.domain_exceptions import (
    PatientNotFoundException,
    DoctorNotFoundException,
    DoctorNotAvailableException,
    AppointmentSlotTakenException,
)


class CreateAppointmentUseCase:
    """
    Caso de uso: agendar una cita médica.

    Validaciones:
      1. El paciente existe.
      2. El médico existe y tiene disponibilidad ese día/hora.
      3. El slot no está ocupado por otra cita activa.
      4. La fecha es futura y dentro del horario laboral
         (validado por la entidad Appointment.create).
    """

    def __init__(
        self,
        appointment_repository: IAppointmentRepository,
        doctor_repository: IDoctorRepository,
        patient_repository: IPatientRepository,
    ) -> None:
        self._appointment_repo = appointment_repository
        self._doctor_repo = doctor_repository
        self._patient_repo = patient_repository

    async def execute(self, dto: CreateAppointmentDTO) -> AppointmentDTO:
        # 1. Verificar que el paciente existe
        patient = await self._patient_repo.find_by_id(dto.patient_id)
        if not patient:
            raise PatientNotFoundException(str(dto.patient_id))

        # 2. Verificar que el médico existe con su disponibilidad
        doctor = await self._doctor_repo.find_by_id_with_availability(dto.doctor_id)
        if not doctor:
            raise DoctorNotFoundException(str(dto.doctor_id))

        # 3. Verificar disponibilidad del médico en ese día/hora
        if not doctor.is_available_at(dto.scheduled_at):
            raise DoctorNotAvailableException(
                str(dto.doctor_id), str(dto.scheduled_at)
            )

        # 4. Verificar que el slot no está tomado
        slot_taken = await self._appointment_repo.exists_slot_taken(
            doctor_id=dto.doctor_id,
            scheduled_at=dto.scheduled_at,
        )
        if slot_taken:
            raise AppointmentSlotTakenException(
                str(dto.doctor_id), str(dto.scheduled_at)
            )

        # 5. Crear la entidad — aquí se validan fecha futura y horario laboral
        appointment = Appointment.create(
            patient_id=dto.patient_id,
            doctor_id=dto.doctor_id,
            scheduled_at=dto.scheduled_at,
            duration_minutes=dto.duration_minutes,
            notes=dto.notes,
        )

        saved = await self._appointment_repo.save(appointment)
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