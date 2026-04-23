from app.domain.ports.appointment_repository import AppointmentRepository


class CancelAppointmentUseCase:

    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    async def execute(self, appointment_id: str):
        appointment = await self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        appointment.cancel()
        await self.appointment_repository.save(appointment)
        return appointment