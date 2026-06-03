from uuid import UUID

from app.application.dtos.patient_dto import PatientDTO
from app.application.ports.output.i_patient_repository import IPatientRepository
from app.domain.entities.patient import Patient
from app.domain.exceptions.domain_exceptions import PatientNotFoundException


class GetPatientByIdUseCase:
    def __init__(self, patient_repository: IPatientRepository) -> None:
        self._repo = patient_repository

    async def execute(self, patient_id: UUID) -> PatientDTO:
        patient = await self._repo.find_by_id(patient_id)
        if not patient:
            raise PatientNotFoundException(str(patient_id))
        return _to_dto(patient)


class GetPatientsUseCase:
    def __init__(self, patient_repository: IPatientRepository) -> None:
        self._repo = patient_repository

    async def execute(self, skip: int = 0, limit: int = 20) -> list[PatientDTO]:
        patients = await self._repo.find_all(skip=skip, limit=limit)
        return [_to_dto(p) for p in patients]


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