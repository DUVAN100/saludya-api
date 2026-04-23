from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.doctor import Doctor, DoctorAvailability


class IDoctorRepository(ABC):
    """
    Puerto de salida — contrato para persistir médicos
    y sus disponibilidades.
    """

    @abstractmethod
    async def save(self, doctor: Doctor) -> Doctor:
        ...

    @abstractmethod
    async def find_by_id(self, doctor_id: UUID) -> Doctor | None:
        ...

    @abstractmethod
    async def find_by_id_with_availability(self, doctor_id: UUID) -> Doctor | None:
        """Retorna el médico con su lista de availability precargada."""
        ...

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> Doctor | None:
        ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[Doctor]:
        ...

    @abstractmethod
    async def find_by_specialty(self, specialty: str) -> list[Doctor]:
        ...

    @abstractmethod
    async def update(self, doctor: Doctor) -> Doctor:
        ...

    @abstractmethod
    async def exists_by_license_number(self, license_number: str) -> bool:
        ...

    @abstractmethod
    async def save_availability(
        self, availability: DoctorAvailability
    ) -> DoctorAvailability:
        ...