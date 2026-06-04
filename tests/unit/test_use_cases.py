from datetime import datetime, time, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.dtos.appointment_dto import CreateAppointmentDTO
from app.application.dtos.auth_dto import LoginDTO
from app.application.dtos.doctor_dto import CreateDoctorDTO
from app.application.dtos.patient_dto import RegisterPatientDTO
from app.application.use_cases.appointment.create_appointment import (
    CreateAppointmentUseCase,
)
from app.application.use_cases.appointment.get_appointment import (
    GetAllAppointmentsUseCase,
    GetAppointmentByIdUseCase,
    GetAppointmentsByDoctorUseCase,
    GetAppointmentsByPatientUseCase,
)
from app.application.use_cases.appointment.update_appointment_status import (
    CancelAppointmentUseCase,
    ConfirmAppointmentUseCase,
)
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.doctor.create_doctor import CreateDoctorUseCase
from app.application.use_cases.doctor.get_doctor import (
    GetDoctorByIdUseCase,
    GetDoctorsUseCase,
)
from app.application.use_cases.patient.get_patient import (
    GetPatientByIdUseCase,
    GetPatientsUseCase,
)
from app.application.use_cases.patient.register_patient import RegisterPatientUseCase
from app.domain.entities.appointment import Appointment
from app.domain.entities.doctor import Doctor, DoctorAvailability
from app.domain.entities.patient import Patient
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    AppointmentNotFoundException,
    AppointmentSlotTakenException,
    DoctorNotAvailableException,
    DoctorNotFoundException,
    InactiveUserException,
    InvalidCredentialsException,
    PatientAlreadyExistsException,
    PatientNotFoundException,
    UserAlreadyExistsException,
)
from app.domain.value_objects.appointment_status import AppointmentStatus
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole


def future_weekday_at(hour: int = 10) -> datetime:
    value = datetime.now(timezone.utc) + timedelta(days=1)
    while value.isoweekday() not in {1, 2, 3, 4, 5}:
        value += timedelta(days=1)
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{plain_password}"


class FakeTokenService:
    def create_access_token(self, payload: dict) -> str:
        return f"token:{payload['sub']}:{payload['role']}"


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self.users = users or []
        self.saved: list[User] = []

    async def save(self, user: User) -> User:
        self.users.append(user)
        self.saved.append(user)
        return user

    async def find_by_id(self, user_id):
        return next((user for user in self.users if user.id == user_id), None)

    async def find_by_email(self, email: str):
        return next((user for user in self.users if user.email.value == email), None)

    async def exists_by_email(self, email: str) -> bool:
        return any(user.email.value == email for user in self.users)

    async def update(self, user: User) -> User:
        return user


class FakePatientRepository:
    def __init__(self, patients: list[Patient] | None = None) -> None:
        self.patients = patients or []
        self.saved: list[Patient] = []

    async def save(self, patient: Patient) -> Patient:
        self.patients.append(patient)
        self.saved.append(patient)
        return patient

    async def find_by_id(self, patient_id):
        return next((patient for patient in self.patients if patient.id == patient_id), None)

    async def find_by_user_id(self, user_id):
        return next((patient for patient in self.patients if patient.user_id == user_id), None)

    async def find_by_document_number(self, document_number: str):
        return next(
            (
                patient
                for patient in self.patients
                if patient.document_number == document_number
            ),
            None,
        )

    async def find_all(self, skip: int = 0, limit: int = 20):
        return self.patients[skip : skip + limit]

    async def update(self, patient: Patient) -> Patient:
        return patient

    async def exists_by_document_number(self, document_number: str) -> bool:
        return any(patient.document_number == document_number for patient in self.patients)


class FakeDoctorRepository:
    def __init__(self, doctors: list[Doctor] | None = None) -> None:
        self.doctors = doctors or []
        self.saved_availability: list[DoctorAvailability] = []

    async def save(self, doctor: Doctor) -> Doctor:
        self.doctors.append(doctor)
        return doctor

    async def find_by_id(self, doctor_id):
        return next((doctor for doctor in self.doctors if doctor.id == doctor_id), None)

    async def find_by_id_with_availability(self, doctor_id):
        return await self.find_by_id(doctor_id)

    async def find_by_user_id(self, user_id):
        return next((doctor for doctor in self.doctors if doctor.user_id == user_id), None)

    async def find_all(self, skip: int = 0, limit: int = 20):
        return self.doctors[skip : skip + limit]

    async def find_by_specialty(self, specialty: str):
        return [doctor for doctor in self.doctors if doctor.specialty == specialty]

    async def update(self, doctor: Doctor) -> Doctor:
        return doctor

    async def exists_by_license_number(self, license_number: str) -> bool:
        return any(doctor.license_number == license_number for doctor in self.doctors)

    async def save_availability(self, availability: DoctorAvailability) -> DoctorAvailability:
        self.saved_availability.append(availability)
        return availability


class FakeAppointmentRepository:
    def __init__(self, appointments: list[Appointment] | None = None) -> None:
        self.appointments = appointments or []
        self.slot_taken = False

    async def save(self, appointment: Appointment) -> Appointment:
        self.appointments.append(appointment)
        return appointment

    async def find_by_id(self, appointment_id):
        return next(
            (appointment for appointment in self.appointments if appointment.id == appointment_id),
            None,
        )

    async def find_by_patient_id(self, patient_id, skip: int = 0, limit: int = 20):
        return [
            appointment
            for appointment in self.appointments
            if appointment.patient_id == patient_id
        ][skip : skip + limit]

    async def find_by_doctor_id(self, doctor_id, skip: int = 0, limit: int = 20):
        return [
            appointment
            for appointment in self.appointments
            if appointment.doctor_id == doctor_id
        ][skip : skip + limit]

    async def find_by_doctor_and_date_range(self, doctor_id, start, end):
        return [
            appointment
            for appointment in self.appointments
            if appointment.doctor_id == doctor_id and start <= appointment.scheduled_at <= end
        ]

    async def exists_slot_taken(self, doctor_id, scheduled_at, exclude_appointment_id=None):
        if self.slot_taken:
            return True
        return any(
            appointment.doctor_id == doctor_id
            and appointment.scheduled_at == scheduled_at
            and appointment.status in {AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED}
            and appointment.id != exclude_appointment_id
            for appointment in self.appointments
        )

    async def update(self, appointment: Appointment) -> Appointment:
        return appointment

    async def find_all(self, status=None, skip: int = 0, limit: int = 20):
        values = self.appointments
        if status:
            values = [appointment for appointment in values if appointment.status == status]
        return values[skip : skip + limit]


def make_user(role: UserRole = UserRole.patient, active: bool = True) -> User:
    return User(
        email=Email(f"{role.value}-{uuid4()}@example.com"),
        password_hash="hashed:Password123!",
        role=role,
        is_active=active,
    )


def make_patient() -> Patient:
    return Patient(
        user_id=uuid4(),
        first_name="Ana",
        last_name="Paciente",
        document_number=f"DOC-{uuid4()}",
    )


def make_doctor(scheduled_at: datetime | None = None) -> Doctor:
    scheduled = scheduled_at or future_weekday_at()
    doctor = Doctor(
        user_id=uuid4(),
        first_name="Carlos",
        last_name="Medico",
        specialty="Cardiologia",
        license_number=f"MED-{uuid4()}",
    )
    doctor.availability.append(
        DoctorAvailability(
            doctor_id=doctor.id,
            day_of_week=scheduled.isoweekday(),
            start_time=time(8, 0),
            end_time=time(17, 0),
        )
    )
    return doctor


@pytest.mark.asyncio
async def test_login_use_case_success():
    user = make_user()
    use_case = LoginUseCase(
        FakeUserRepository([user]),
        FakePasswordHasher(),
        FakeTokenService(),
    )

    result = await use_case.execute(LoginDTO(user.email.value, "Password123!"))

    assert result.access_token.startswith("token:")
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_use_case_rejects_unknown_wrong_and_inactive_users():
    user = make_user(active=False)
    use_case = LoginUseCase(FakeUserRepository([user]), FakePasswordHasher(), FakeTokenService())

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(LoginDTO("missing@example.com", "Password123!"))

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(LoginDTO(user.email.value, "wrong"))

    with pytest.raises(InactiveUserException):
        await use_case.execute(LoginDTO(user.email.value, "Password123!"))


@pytest.mark.asyncio
async def test_register_patient_use_case_success_and_conflicts():
    user_repo = FakeUserRepository()
    patient_repo = FakePatientRepository()
    use_case = RegisterPatientUseCase(user_repo, patient_repo, FakePasswordHasher())

    result = await use_case.execute(
        RegisterPatientDTO(
            email="patient@example.com",
            password="Password123!",
            first_name="Ana",
            last_name="Paciente",
            document_number="DOC-1",
        )
    )

    assert result.full_name == "Ana Paciente"
    assert user_repo.saved[0].role == UserRole.patient

    with pytest.raises(UserAlreadyExistsException):
        await use_case.execute(
            RegisterPatientDTO(
                email="patient@example.com",
                password="Password123!",
                first_name="Ana",
                last_name="Paciente",
            )
        )

    with pytest.raises(PatientAlreadyExistsException):
        await use_case.execute(
            RegisterPatientDTO(
                email="other@example.com",
                password="Password123!",
                first_name="Ana",
                last_name="Paciente",
                document_number="DOC-1",
            )
        )


@pytest.mark.asyncio
async def test_get_patient_use_cases():
    patient = make_patient()
    repo = FakePatientRepository([patient])

    result = await GetPatientByIdUseCase(repo).execute(patient.id)
    results = await GetPatientsUseCase(repo).execute()

    assert result.id == patient.id
    assert len(results) == 1

    with pytest.raises(PatientNotFoundException):
        await GetPatientByIdUseCase(repo).execute(uuid4())


@pytest.mark.asyncio
async def test_create_doctor_use_case_success_and_conflicts():
    user_repo = FakeUserRepository()
    doctor_repo = FakeDoctorRepository()
    use_case = CreateDoctorUseCase(user_repo, doctor_repo, FakePasswordHasher())

    result = await use_case.execute(
        CreateDoctorDTO(
            email="doctor@example.com",
            password="Password123!",
            first_name="Carlos",
            last_name="Medico",
            specialty="Cardiologia",
            license_number="MED-1",
        )
    )

    assert result.full_name == "Dr. Carlos Medico"
    assert len(result.availability) == 5
    assert user_repo.saved[0].role == UserRole.doctor

    with pytest.raises(UserAlreadyExistsException):
        await use_case.execute(
            CreateDoctorDTO(
                email="doctor@example.com",
                password="Password123!",
                first_name="Carlos",
                last_name="Medico",
                specialty="Cardiologia",
                license_number="MED-2",
            )
        )

    with pytest.raises(ValueError):
        await use_case.execute(
            CreateDoctorDTO(
                email="other-doctor@example.com",
                password="Password123!",
                first_name="Carlos",
                last_name="Medico",
                specialty="Cardiologia",
                license_number="MED-1",
            )
        )


@pytest.mark.asyncio
async def test_get_doctor_use_cases():
    doctor = make_doctor()
    repo = FakeDoctorRepository([doctor])

    result = await GetDoctorByIdUseCase(repo).execute(doctor.id)
    results = await GetDoctorsUseCase(repo).execute()

    assert result.id == doctor.id
    assert len(results) == 1

    with pytest.raises(DoctorNotFoundException):
        await GetDoctorByIdUseCase(repo).execute(uuid4())


@pytest.mark.asyncio
async def test_create_appointment_use_case_success_and_errors():
    scheduled_at = future_weekday_at()
    patient = make_patient()
    doctor = make_doctor(scheduled_at)
    appointment_repo = FakeAppointmentRepository()
    patient_repo = FakePatientRepository([patient])
    doctor_repo = FakeDoctorRepository([doctor])
    use_case = CreateAppointmentUseCase(appointment_repo, doctor_repo, patient_repo)

    result = await use_case.execute(
        CreateAppointmentDTO(patient.id, doctor.id, scheduled_at, notes="Consulta")
    )

    assert result.patient_id == patient.id
    assert result.doctor_id == doctor.id
    assert result.status == AppointmentStatus.PENDING

    with pytest.raises(PatientNotFoundException):
        await use_case.execute(CreateAppointmentDTO(uuid4(), doctor.id, scheduled_at))

    with pytest.raises(DoctorNotFoundException):
        await use_case.execute(CreateAppointmentDTO(patient.id, uuid4(), scheduled_at))

    unavailable_doctor = make_doctor(scheduled_at)
    unavailable_doctor.availability.clear()
    with pytest.raises(DoctorNotAvailableException):
        await CreateAppointmentUseCase(
            FakeAppointmentRepository(),
            FakeDoctorRepository([unavailable_doctor]),
            patient_repo,
        ).execute(CreateAppointmentDTO(patient.id, unavailable_doctor.id, scheduled_at))

    occupied_repo = FakeAppointmentRepository()
    occupied_repo.slot_taken = True
    with pytest.raises(AppointmentSlotTakenException):
        await CreateAppointmentUseCase(
            occupied_repo,
            doctor_repo,
            patient_repo,
        ).execute(CreateAppointmentDTO(patient.id, doctor.id, scheduled_at))


@pytest.mark.asyncio
async def test_get_appointment_use_cases_and_status_filter():
    patient_id = uuid4()
    doctor_id = uuid4()
    appointment = Appointment.create(patient_id, doctor_id, future_weekday_at())
    confirmed = Appointment.create(patient_id, doctor_id, future_weekday_at(hour=11))
    confirmed.confirm()
    repo = FakeAppointmentRepository([appointment, confirmed])

    assert (await GetAppointmentByIdUseCase(repo).execute(appointment.id)).id == appointment.id
    assert len(await GetAppointmentsByPatientUseCase(repo).execute(patient_id)) == 2
    assert len(await GetAppointmentsByDoctorUseCase(repo).execute(doctor_id)) == 2
    assert len(await GetAllAppointmentsUseCase(repo).execute()) == 2
    assert len(await GetAllAppointmentsUseCase(repo).execute(AppointmentStatus.CONFIRMED)) == 1

    with pytest.raises(AppointmentNotFoundException):
        await GetAppointmentByIdUseCase(repo).execute(uuid4())


@pytest.mark.asyncio
async def test_confirm_and_cancel_appointment_use_cases():
    appointment = Appointment.create(uuid4(), uuid4(), future_weekday_at())
    repo = FakeAppointmentRepository([appointment])

    confirmed = await ConfirmAppointmentUseCase(repo).execute(appointment.id)
    cancelled = await CancelAppointmentUseCase(repo).execute(appointment.id)

    assert confirmed.status == AppointmentStatus.CONFIRMED
    assert cancelled.status == AppointmentStatus.CANCELLED

    with pytest.raises(AppointmentNotFoundException):
        await ConfirmAppointmentUseCase(repo).execute(uuid4())

    with pytest.raises(AppointmentNotFoundException):
        await CancelAppointmentUseCase(repo).execute(uuid4())
