from enum import Enum


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

    def can_transition_to(self, new_status: "AppointmentStatus") -> bool:
        allowed: dict[AppointmentStatus, set[AppointmentStatus]] = {
            AppointmentStatus.PENDING: {
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.CANCELLED,
            },
            AppointmentStatus.CONFIRMED: {
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED,
                AppointmentStatus.NO_SHOW,
            },
            AppointmentStatus.CANCELLED: set(),
            AppointmentStatus.COMPLETED: set(),
            AppointmentStatus.NO_SHOW: set(),
        }
        return new_status in allowed[self]