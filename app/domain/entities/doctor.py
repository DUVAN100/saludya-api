from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from uuid import UUID, uuid4


@dataclass
class DoctorAvailability:
    doctor_id: UUID
    day_of_week: int          # 1 = Monday … 5 = Friday
    start_time: time
    end_time: time
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True

    def covers(self, check_time: time) -> bool:
        return self.is_active and self.start_time <= check_time < self.end_time


@dataclass
class Doctor:
    user_id: UUID
    first_name: str
    last_name: str
    specialty: str
    license_number: str
    id: UUID = field(default_factory=uuid4)
    phone: str | None = None
    consultation_duration: int = 30   # minutes
    availability: list[DoctorAvailability] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def full_name(self) -> str:
        return f"Dr. {self.first_name} {self.last_name}"

    def is_available_at(self, scheduled_at: datetime) -> bool:
        """
        Returns True if the doctor has an active availability slot
        covering the given datetime (Mon–Fri, within defined hours).
        """
        weekday = scheduled_at.isoweekday()   # 1 = Monday, 7 = Sunday
        slot_time = scheduled_at.time()

        return any(
            avail.day_of_week == weekday and avail.covers(slot_time)
            for avail in self.availability
        )