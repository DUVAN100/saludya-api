from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.patient import Patient


class IPatientRepository(ABC):
    """
    Puerto de salida — contrato que la infraestructura debe cumplir
    para persistir y recuperar pacientes.
    """

    @abstractmethod
    async def save(self, patient: Patient) -> Patient:
        ...

    @abstractmethod
    async def find_by_id(self, patient_id: UUID) -> Patient | None:
        ...

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> Patient | None:
        ...

    @abstractmethod
    async def find_by_document_number(self, document_number: str) -> Patient | None:
        ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[Patient]:
        ...

    @abstractmethod
    async def update(self, patient: Patient) -> Patient:
        ...

    @abstractmethod
    async def exists_by_document_number(self, document_number: str) -> bool:
        ...