from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User


class IUserRepository(ABC):
    """
    Puerto de salida — define QUÉ operaciones necesita el dominio
    para persistir usuarios. La infraestructura decide el CÓMO.
    """

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persiste un usuario nuevo y lo retorna con datos generados por la DB."""
        ...

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None:
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...