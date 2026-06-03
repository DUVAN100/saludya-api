from app.application.dtos.doctor_dto import CreateDoctorDTO, DoctorDTO, DoctorAvailabilityDTO
from app.application.ports.output.i_user_repository import IUserRepository
from app.application.ports.output.i_doctor_repository import IDoctorRepository
from app.domain.entities.doctor import Doctor, DoctorAvailability
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    UserAlreadyExistsException,
    DoctorNotFoundException,
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole
from datetime import time


_DEFAULT_AVAILABILITY = [
    (1, time(8, 0), time(17, 0)),
    (2, time(8, 0), time(17, 0)),
    (3, time(8, 0), time(17, 0)),
    (4, time(8, 0), time(17, 0)),
    (5, time(8, 0), time(17, 0)),
]


class CreateDoctorUseCase:
    """
    Caso de uso: crear un médico nuevo.
    Crea el usuario, el perfil del médico y su disponibilidad
    fija lun–vie 08:00–17:00 de forma automática.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        doctor_repository: IDoctorRepository,
        password_hasher,
    ) -> None:
        self._user_repo = user_repository
        self._doctor_repo = doctor_repository
        self._hasher = password_hasher

    async def execute(self, dto: CreateDoctorDTO) -> DoctorDTO:
        email = Email(dto.email)

        if await self._user_repo.exists_by_email(email.value):
            raise UserAlreadyExistsException(email.value)

        if await self._doctor_repo.exists_by_license_number(dto.license_number):
            raise ValueError(f"License number '{dto.license_number}' already registered")

        # Crear entidades
        user = User(
            email=email,
            password_hash=self._hasher.hash(dto.password),
            role=UserRole.doctor,
        )
        doctor = Doctor(
            user_id=user.id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            specialty=dto.specialty,
            license_number=dto.license_number,
            phone=dto.phone,
            consultation_duration=dto.consultation_duration,
        )

        # Persistir
        await self._user_repo.save(user)
        saved_doctor = await self._doctor_repo.save(doctor)

        # Crear disponibilidad fija lun–vie
        for day, start, end in _DEFAULT_AVAILABILITY:
            avail = DoctorAvailability(
                doctor_id=saved_doctor.id,
                day_of_week=day,
                start_time=start,
                end_time=end,
            )
            saved_avail = await self._doctor_repo.save_availability(avail)
            saved_doctor.availability.append(saved_avail)

        return _to_dto(saved_doctor)


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