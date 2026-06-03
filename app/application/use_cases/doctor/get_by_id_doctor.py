from app.domain.ports.doctor_repository import DoctorRepository


class GetDoctorByIdUseCase:

    def __init__(self, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    async def execute(self, doctor_id: str):
        doctor = await self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError(f"Doctor with id {doctor_id} not found")
        return doctor