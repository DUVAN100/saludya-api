"""
Script para cargar datos de prueba en la base de datos
Ejecutar: python scripts/seed_db.py
"""

import asyncio
import uuid
from datetime import datetime, timezone, date, time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.doctor_model import DoctorModel, DoctorAvailabilityModel
from app.infrastructure.persistence.models.patient_model import PatientModel
from app.infrastructure.persistence.models.appointment_model import AppointmentModel
from app.infrastructure.security.password_hasher import PasswordHasher
from app.domain.value_objects.appointment_status import AppointmentStatus


async def seed_database():
    """Inserta datos de prueba en la base de datos"""
    
    # ─── Configurar engine y sesión ────────────────────────────────────────
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    hasher = PasswordHasher()
    
    print("🌱 Iniciando seed de datos...")
    
    async with async_session() as session:
        try:
            # Crear tablas si no existen
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas/verificadas")
            
            # ─── 1. ADMIN ──────────────────────────────────────────────────────
            admin_user = UserModel(
                id=uuid.uuid4(),
                email="admin@example.com",
                password_hash=hasher.hash_password("Admin123!"),
                role="admin",
                is_active=True,
            )
            session.add(admin_user)
            await session.flush()
            print(f"✅ Admin creado: admin@example.com")
            
            # ─── 2. DOCTOR ────────────────────────────────────────────────────
            doctor_user = UserModel(
                id=uuid.uuid4(),
                email="doctor@example.com",
                password_hash=hasher.hash_password("Doctor123!"),
                role="doctor",
                is_active=True,
            )
            session.add(doctor_user)
            await session.flush()
            print(f"✅ Usuario doctor creado: doctor@example.com")
            
            doctor = DoctorModel(
                id=uuid.uuid4(),
                user_id=doctor_user.id,
                first_name="Juan",
                last_name="Pérez García",
                specialty="Cardiología",
                license_number="LIC-2024-001",
                phone="+34-600-123-456",
                consultation_duration=30,
            )
            session.add(doctor)
            await session.flush()
            print(f"✅ Perfil doctor creado: {doctor.first_name} {doctor.last_name} ({doctor.specialty})")
            
            # Agregar disponibilidad del doctor (lunes a viernes, 8am-5pm)
            for day in range(1, 6):  # 1=Lunes, 5=Viernes
                availability = DoctorAvailabilityModel(
                    id=uuid.uuid4(),
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(8, 0),
                    end_time=time(17, 0),
                    is_active=True,
                )
                session.add(availability)
            await session.flush()
            print(f"✅ Disponibilidad del doctor configurada")
            
            # ─── 3. PACIENTE ──────────────────────────────────────────────────
            patient_user = UserModel(
                id=uuid.uuid4(),
                email="patient@example.com",
                password_hash=hasher.hash_password("Patient123!"),
                role="patient",
                is_active=True,
            )
            session.add(patient_user)
            await session.flush()
            print(f"✅ Usuario paciente creado: patient@example.com")
            
            patient = PatientModel(
                id=uuid.uuid4(),
                user_id=patient_user.id,
                first_name="María",
                last_name="López Rodríguez",
                birth_date=date(1990, 3, 15),
                phone="+34-600-987-654",
                document_number="12345678A",
                document_type="DNI",
                gender="F",
                address="Calle Principal 123, Madrid",
            )
            session.add(patient)
            await session.flush()
            print(f"✅ Perfil paciente creado: {patient.first_name} {patient.last_name}")
            
            # ─── 4. CITA DE PRUEBA ─────────────────────────────────────────────
            appointment = AppointmentModel(
                id=uuid.uuid4(),
                patient_id=patient.id,
                doctor_id=doctor.id,
                scheduled_at=datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc),
                duration_minutes=30,
                status=AppointmentStatus.PENDING,
                notes="Revisión general de cardiología",
            )
            session.add(appointment)
            await session.flush()
            print(f"✅ Cita creada para {patient.first_name} {patient.last_name} con {doctor.first_name} {doctor.last_name}")
            
            # Commit
            await session.commit()
            print("\n✅ ¡Seed completado exitosamente!\n")
            print("📋 Datos de prueba:")
            print(f"   Admin  : admin@example.com / Admin123!")
            print(f"   Doctor : doctor@example.com / Doctor123!")
            print(f"   Patient: patient@example.com / Patient123!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante seed: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
