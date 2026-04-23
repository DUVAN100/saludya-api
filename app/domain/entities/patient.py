from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Patient:
    user_id: UUID
    first_name: str
    last_name: str
    id: UUID = field(default_factory=uuid4)
    birth_date: date | None = None
    phone: str | None = None
    document_number: str | None = None
    document_type: str | None = None
    gender: str | None = None
    address: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )