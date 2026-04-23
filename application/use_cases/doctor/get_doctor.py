from uuid import UUID

from app.application.dtos.doctor_dto import DoctorDTO, DoctorAvailabilityDTO
from app.application.ports.output.i_doctor_repository import IDoctorRepository
from app.domain.entities.doctor import Doctor
from app.domain.exceptions.domain_exceptions import DoctorNotFoundException


class GetDoctorByIdUseCase:
    def __init__(self, doctor_repository: IDoctorRepository) -> None:
        self._repo = doctor_repository

    async def execute(self, doctor_id: UUID) -> DoctorDTO:
        doctor = await self._repo.find_by_id_with_availability(doctor_id)
        if not doctor:
            raise DoctorNotFoundException(str(doctor_id))
        return _to_dto(doctor)


class GetDoctorsUseCase:
    def __init__(self, doctor_repository: IDoctorRepository) -> None:
        self._repo = doctor_repository

    async def execute(self, skip: int = 0, limit: int = 20) -> list[DoctorDTO]:
        doctors = await self._repo.find_all(skip=skip, limit=limit)
        return [_to_dto(d) for d in doctors]


def _to_dto(doctor: Doctor) -> DoctorDTO:
    return DoctorDTO(
        id=doctor.id,
        user_id=doctor.user_id,
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        full_name=doctor.full_name,
        specialty=doctor.specialty,
        license_number=doctor.license_number,
        phone=doctor.phone,
        consultation_duration=doctor.consultation_duration,
        availability=[
            DoctorAvailabilityDTO(
                id=a.id,
                day_of_week=a.day_of_week,
                start_time=a.start_time,
                end_time=a.end_time,
                is_active=a.is_active,
            )
            for a in doctor.availability
        ],
        created_at=doctor.created_at,
    )