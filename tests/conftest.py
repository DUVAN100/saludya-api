import asyncio
import os
from collections.abc import AsyncGenerator
from datetime import datetime, time, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/saludya_test",
    ),
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("APP_NAME", "Saludya Test API")
os.environ.setdefault("APP_VERSION", "test")
os.environ.setdefault("DEBUG", "True")

from app.adapters.http.dependencies import get_current_user  # noqa: E402
from app.domain.value_objects.appointment_status import AppointmentStatus  # noqa: E402
from app.domain.value_objects.user_role import UserRole  # noqa: E402
from app.infrastructure.persistence.database import Base, get_db_session  # noqa: E402
from app.infrastructure.persistence.models.appointment_model import AppointmentModel  # noqa: E402
from app.infrastructure.persistence.models.doctor_model import DoctorAvailabilityModel, DoctorModel  # noqa: E402
from app.infrastructure.persistence.models.patient_model import PatientModel  # noqa: E402
from app.infrastructure.persistence.models.user_model import UserModel  # noqa: E402
from app.infrastructure.security.jwt_handler import JWTHandler  # noqa: E402
from app.infrastructure.security.password_hasher import PasswordHasher  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)

TestingSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db_session] = override_get_db_session


# ── Schema: sync fixture, usa asyncio.run() para no conflicto de loop ─────
@pytest.fixture(scope="session", autouse=True)
def database_schema():
    async def _create():
        async with test_engine.begin() as conn:
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_type WHERE typname = 'appointment_status'
                    ) THEN
                        CREATE TYPE appointment_status AS ENUM (
                            'pending', 'confirmed', 'cancelled', 'completed', 'no_show'
                        );
                    END IF;
                END $$;
            """))
            await conn.run_sync(Base.metadata.create_all)

    async def _drop():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.execute(text("DROP TYPE IF EXISTS appointment_status"))
        await test_engine.dispose()

    asyncio.run(_create())
    yield
    asyncio.run(_drop())


# ── Limpia tablas antes de cada test ──────────────────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    async with test_engine.begin() as conn:
        await conn.execute(text("""
            TRUNCATE TABLE
                appointments, doctor_availability, doctors, patients, users
            RESTART IDENTITY CASCADE
        """))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionFactory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return PasswordHasher()


@pytest.fixture
def jwt_handler() -> JWTHandler:
    return JWTHandler()


# ── Helpers internos ───────────────────────────────────────────────────────
async def _create_user(
    session: AsyncSession,
    *,
    email: str,
    password: str = "Password123!",
    role: UserRole = UserRole.patient,
    is_active: bool = True,
) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=email,
        password_hash=PasswordHasher().hash(password),
        role=role.value,
        is_active=is_active,
    )
    session.add(user)
    await session.flush()
    return user


async def _create_patient(
    session: AsyncSession,
    *,
    email: str = "patient@example.com",
    password: str = "Password123!",
    first_name: str = "Ana",
    last_name: str = "Paciente",
    document_number: str = "PAT-001",
) -> PatientModel:
    user = await _create_user(session, email=email, password=password, role=UserRole.patient)
    patient = PatientModel(
        id=uuid4(),
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        document_number=document_number,
        document_type="CC",
        gender="F",
    )
    session.add(patient)
    await session.flush()
    return patient


async def _create_doctor(
    session: AsyncSession,
    *,
    email: str = "doctor@example.com",
    password: str = "Password123!",
    first_name: str = "Carlos",
    last_name: str = "Medico",
    specialty: str = "Cardiologia",
    license_number: str = "MED-001",
) -> DoctorModel:
    user = await _create_user(session, email=email, password=password, role=UserRole.doctor)
    doctor = DoctorModel(
        id=uuid4(),
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        license_number=license_number,
        consultation_duration=30,
    )
    session.add(doctor)
    await session.flush()
    for day in range(1, 6):
        session.add(DoctorAvailabilityModel(
            id=uuid4(),
            doctor_id=doctor.id,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(17, 0),
            is_active=True,
        ))
    await session.flush()
    return doctor


async def _create_appointment(
    session: AsyncSession,
    *,
    patient_id,
    doctor_id,
    scheduled_at: datetime,
    status: AppointmentStatus = AppointmentStatus.PENDING,
) -> AppointmentModel:
    appointment = AppointmentModel(
        id=uuid4(),
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_at=scheduled_at,
        duration_minutes=30,
        status=status,
        notes="Test appointment",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(appointment)
    await session.flush()
    return appointment


def auth_header_for(role: UserRole = UserRole.admin, sub: str | None = None) -> dict[str, str]:
    token = JWTHandler().create_access_token(
        {"sub": sub or str(uuid4()), "role": role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_factory():
    return auth_header_for


# ── Fixtures de creación para e2e/integration ─────────────────────────────
@pytest.fixture
def create_user(db_session):
    async def _inner(**kwargs):
        return await _create_user(db_session, **kwargs)
    return _inner


@pytest.fixture
def create_patient(db_session):
    async def _inner(**kwargs):
        return await _create_patient(db_session, **kwargs)
    return _inner


@pytest.fixture
def create_doctor(db_session):
    async def _inner(**kwargs):
        return await _create_doctor(db_session, **kwargs)
    return _inner


@pytest.fixture
def current_user_override_factory():
    def override(role: UserRole = UserRole.admin, sub: str | None = None):
        from app.application.dtos.auth_dto import TokenPayloadDTO
        app.dependency_overrides[get_current_user] = lambda: TokenPayloadDTO(
            sub=sub or str(uuid4()),
            role=role,
        )
        return app.dependency_overrides
    yield override
    app.dependency_overrides.pop(get_current_user, None)