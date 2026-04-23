from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole


@dataclass
class User:
    email: Email
    password_hash: str
    role: UserRole
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def deactivate(self) -> None:
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        self.is_active = True
        self._touch()

    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    def is_doctor(self) -> bool:
        return self.role == UserRole.doctor

    def is_patient(self) -> bool:
        return self.role == UserRole.patient

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)