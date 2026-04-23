from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.appointment import Appointment
from app.domain.value_objects.appointment_status import AppointmentStatus


class IAppointmentRepository(ABC):
    """
    Puerto de salida — contrato para persistir citas médicas
    y realizar las consultas necesarias para el agendamiento.
    """

    @abstractmethod
    async def save(self, appointment: Appointment) -> Appointment:
        ...

    @abstractmethod
    async def find_by_id(self, appointment_id: UUID) -> Appointment | None:
        ...

    @abstractmethod
    async def find_by_patient_id(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        ...

    @abstractmethod
    async def find_by_doctor_id(
        self,
        doctor_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        ...

    @abstractmethod
    async def find_by_doctor_and_date_range(
        self,
        doctor_id: UUID,
        start: datetime,
        end: datetime,
    ) -> list[Appointment]:
        """Usado para calcular slots disponibles del médico."""
        ...

    @abstractmethod
    async def exists_slot_taken(
        self,
        doctor_id: UUID,
        scheduled_at: datetime,
        exclude_appointment_id: UUID | None = None,
    ) -> bool:
        """
        Verifica si el médico ya tiene una cita activa en ese horario exacto.
        exclude_appointment_id se usa al reagendar para no bloquearse a sí misma.
        """
        ...

    @abstractmethod
    async def update(self, appointment: Appointment) -> Appointment:
        ...

    @abstractmethod
    async def find_all(
        self,
        status: AppointmentStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        """Para el panel administrativo."""
        ...