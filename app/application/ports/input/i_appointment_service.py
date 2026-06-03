from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dtos.appointment_dto import (
    AppointmentDTO,
    CreateAppointmentDTO,
)
from app.domain.value_objects.appointment_status import AppointmentStatus


class IAppointmentService(ABC):
    """
    Puerto de entrada — interfaz que expone las operaciones
    de citas hacia los adaptadores de entrada (HTTP, CLI, etc).
    """

    @abstractmethod
    async def create(self, dto: CreateAppointmentDTO) -> AppointmentDTO:
        ...

    @abstractmethod
    async def confirm(self, appointment_id: UUID) -> AppointmentDTO:
        ...

    @abstractmethod
    async def cancel(self, appointment_id: UUID) -> AppointmentDTO:
        ...

    @abstractmethod
    async def get_by_id(self, appointment_id: UUID) -> AppointmentDTO:
        ...

    @abstractmethod
    async def get_by_patient(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentDTO]:
        ...

    @abstractmethod
    async def get_by_doctor(
        self,
        doctor_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentDTO]:
        ...

    @abstractmethod
    async def get_all(
        self,
        status: AppointmentStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentDTO]:
        ...