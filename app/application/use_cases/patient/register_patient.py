from app.application.dtos.patient_dto import PatientDTO, RegisterPatientDTO
from app.application.ports.output.i_user_repository import IUserRepository
from app.application.ports.output.i_patient_repository import IPatientRepository
from app.domain.entities.patient import Patient
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    UserAlreadyExistsException,
    PatientAlreadyExistsException,
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole


class RegisterPatientUseCase:
    """
    Caso de uso: registrar un paciente nuevo.
    Crea el usuario de autenticación y el perfil del paciente en una operación.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        patient_repository: IPatientRepository,
        password_hasher,           # puerto implícito — cualquier objeto con .hash(pwd)
    ) -> None:
        self._user_repo = user_repository
        self._patient_repo = patient_repository
        self._hasher = password_hasher

    async def execute(self, dto: RegisterPatientDTO) -> PatientDTO:
        # 1. Validar email como value object
        email = Email(dto.email)

        # 2. Verificar que el email no exista ya
        if await self._user_repo.exists_by_email(email.value):
            raise UserAlreadyExistsException(email.value)

        # 3. Verificar documento único si fue enviado
        if dto.document_number and await self._patient_repo.exists_by_document_number(
            dto.document_number
        ):
            raise PatientAlreadyExistsException(dto.document_number)

        # 4. Crear entidades de dominio
        user = User(
            email=email,
            password_hash=self._hasher.hash(dto.password),
            role=UserRole.patient,
        )
        patient = Patient(
            user_id=user.id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            birth_date=dto.birth_date,
            phone=dto.phone,
            document_number=dto.document_number,
            document_type=dto.document_type,
            gender=dto.gender,
            address=dto.address,
        )

        # 5. Persistir (el orden importa: user primero por FK)
        saved_user = await self._user_repo.save(user)
        saved_patient = await self._patient_repo.save(patient)

        return _to_dto(saved_patient)


def _to_dto(patient: Patient) -> PatientDTO:
    return PatientDTO(
        id=patient.id,
        user_id=patient.user_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        full_name=patient.full_name,
        birth_date=patient.birth_date,
        age=patient.age,
        phone=patient.phone,
        document_number=patient.document_number,
        document_type=patient.document_type,
        gender=patient.gender,
        address=patient.address,
        created_at=patient.created_at,
    )