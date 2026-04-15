# 🏥 Saludya API

> **Sistema de Gestión de Citas Médicas** - API REST para coordinar servicios de salud entre pacientes y médicos.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/JWT-Authentication-orange.svg)](https://jwt.io/)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean-purple.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## 📋 Tabla de Contenidos

- [🏥 Saludya API](#-saludya-api)
  - [📋 Tabla de Contenidos](#-tabla-de-contenidos)
  - [🎯 ¿Qué es Saludya?](#-qué-es-saludya)
  - [✨ Características Principales](#-características-principales)
  - [🏗️ Arquitectura](#️-arquitectura)
  - [🚀 Inicio Rápido](#-inicio-rápido)
  - [📚 Documentación API](#-documentación-api)
  - [🔧 Configuración](#-configuración)
  - [🧪 Testing](#-testing)
  - [📁 Estructura del Proyecto](#-estructura-del-proyecto)
  - [🔐 Autenticación](#-autenticación)
  - [📡 Endpoints Principales](#-endpoints-principales)
  - [🗄️ Base de Datos](#️-base-de-datos)
  - [🐳 Docker](#-docker)
  - [📊 Scripts Útiles](#-scripts-útiles)
  - [🤝 Contribución](#-contribución)
  - [📄 Licencia](#-licencia)

---

## 🎯 ¿Qué es Saludya?

**Saludya** es una plataforma backend que revoluciona la gestión de citas médicas tradicionales:

### ❌ Problemas Tradicionales
- Pacientes llaman para agendar citas
- Médicos manejan agendas en papel
- No hay control de disponibilidad en tiempo real
- Difícil escalar para múltiples clínicas

### ✅ Solución Saludya
- ✅ **Agendamiento online** 24/7
- ✅ **Control de disponibilidad** automático
- ✅ **Historial digital** de citas
- ✅ **Roles y permisos** claros
- ✅ **Escalable** y automatizado

---

## ✨ Características Principales

### 👥 Gestión de Usuarios
- **3 Roles**: Administrador, Médico, Paciente
- **Registro seguro** con validaciones
- **Autenticación JWT** con expiración
- **Passwords hasheadas** con bcrypt

### 📅 Sistema de Citas
- **Agendamiento inteligente** con validaciones
- **Control de horarios** (08:00-17:00, lun-vie)
- **Prevención de doble booking**
- **Estados de cita**: PENDING → CONFIRMED → CANCELLED
- **Historial completo** por paciente/médico

### 🏥 Gestión Médica
- **Especialidades médicas**
- **Disponibilidad por médico**
- **Duración de consultas** configurable
- **Licencias profesionales**

### 🔒 Seguridad
- **JWT Authentication** con refresh tokens
- **CORS configurado** para frontend
- **Validaciones en múltiples capas**
- **Protección contra SQL injection**

---

## 🏗️ Arquitectura

### Clean Architecture (Capas)

```
┌─────────────────────────────────────────┐
│   ADAPTERS LAYER (HTTP)                 │
│   - FastAPI Routes & Schemas            │
│   - Exception Handlers                  │
│   - Dependencies Injection              │
└──────────────┬──────────────────────────┘
               │ (Dependency Inversion)
┌──────────────▼──────────────────────────┐
│   APPLICATION LAYER                     │
│   - Use Cases (Business Logic)          │
│   - DTOs (Data Transfer Objects)        │
│   - Ports (Interfaces)                  │
└──────────────┬──────────────────────────┘
               │ (Dependency Inversion)
┌──────────────▼──────────────────────────┐
│   DOMAIN LAYER                          │
│   - Entities (Pure Business)            │
│   - Value Objects                       │
│   - Domain Exceptions                   │
└──────────────┬──────────────────────────┘
               │ (Implementation Details)
┌──────────────▼──────────────────────────┐
│   INFRASTRUCTURE LAYER                  │
│   - SQLAlchemy Models                   │
│   - Repository Implementations          │
│   - JWT Handler & Password Hasher       │
│   - Database Configuration              │
└─────────────────────────────────────────┘
```

### Patrones Implementados

- **Repository Pattern**: Abstracción de acceso a datos
- **Use Case Pattern**: Encapsulación de lógica de negocio
- **Dependency Injection**: Inversión de dependencias
- **DTO Pattern**: Transferencia de datos entre capas
- **Value Objects**: Objetos inmutables con validaciones

---

## 🚀 Inicio Rápido

### Prerrequisitos

- **Python 3.10+**
- **PostgreSQL 15+**
- **Git**

### 1. Clonar Repositorio

```bash
git clone https://github.com/your-username/saludya-api.git
cd saludya-api
```

### 2. Configurar Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

```bash
# Crear base de datos en PostgreSQL
createdb saludya_db

# O usar Docker
docker run --name postgres-saludya -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

### 5. Configurar Variables de Entorno

Crear archivo `.env` en la raíz:

```env
# Base de Datos
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/saludya_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# App
APP_NAME=Saludya Health Appointments API
APP_VERSION=0.1.0
DEBUG=True
```

### 6. Ejecutar Migraciones (si existen)

```bash
# Si tienes Alembic configurado
alembic upgrade head
```

### 7. Poblar Base de Datos (Opcional)

```bash
python scripts/seed_db.py
```

### 8. Ejecutar Servidor

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 9. Verificar Instalación

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health (si implementado)

---

## 📚 Documentación API

### Documentación Interactiva

Una vez ejecutado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Colección Postman

Importa `Saludya_API.postman_collection.json` para testing completo.

### Endpoints Principales

```
POST   /api/v1/auth/login           # Autenticación
GET    /api/v1/doctors              # Listar médicos
POST   /api/v1/doctors              # Crear médico (admin)
GET    /api/v1/patients             # Listar pacientes (admin)
POST   /api/v1/patients             # Registrar paciente
POST   /api/v1/appointments         # Agendar cita
GET    /api/v1/appointments         # Listar citas (admin/doctor)
PATCH  /api/v1/appointments/{id}/confirm  # Confirmar cita
PATCH  /api/v1/appointments/{id}/cancel   # Cancelar cita
```

---

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Default | Requerido |
|----------|-------------|---------|-----------|
| `DATABASE_URL` | URL de conexión PostgreSQL | - | ✅ |
| `JWT_SECRET_KEY` | Clave secreta para JWT | - | ✅ |
| `JWT_ALGORITHM` | Algoritmo JWT | HS256 | ❌ |
| `JWT_EXPIRE_MINUTES` | Expiración token (min) | 60 | ❌ |
| `APP_NAME` | Nombre de la aplicación | Saludya API | ❌ |
| `APP_VERSION` | Versión de la app | 0.1.0 | ❌ |
| `DEBUG` | Modo debug | False | ❌ |

### Configuración de Producción

```env
DATABASE_URL=postgresql+asyncpg://user:password@prod-host:5432/saludya_prod
JWT_SECRET_KEY=your-production-secret-key-minimum-32-characters-long
DEBUG=False
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_auth.py
pytest tests/test_appointments.py

# Con cobertura
pytest --cov=app --cov-report=html
```

### Tests de Integración

```bash
# Tests con BD real
pytest tests/integration/ -v

# Tests con BD en memoria
pytest tests/unit/ -v
```

### Testing con Postman

1. Importar colección: `Saludya_API.postman_collection.json`
2. Ejecutar requests en orden:
   - Login → Crear/Listar → Appointments

---

## 📁 Estructura del Proyecto

```
saludya-api/
│
├── app/                             # Código principal
│   ├── domain/                      # ⭐ Núcleo del negocio
│   │   ├── entities/                # User, Doctor, Patient, Appointment
│   │   ├── value_objects/           # Email, UserRole, AppointmentStatus
│   │   └── exceptions/              # Domain exceptions
│   │
│   ├── application/                 # 🔄 Lógica de aplicación
│   │   ├── use_cases/               # Login, CreateAppointment, etc.
│   │   ├── dtos/                    # Data Transfer Objects
│   │   └── ports/                   # Interfaces (IAppointmentRepository)
│   │
│   ├── adapters/                    # 🔌 Adaptadores externos
│   │   └── http/
│   │       ├── routes/              # FastAPI endpoints
│   │       ├── schemas/             # Pydantic schemas
│   │       ├── dependencies.py      # Auth & DB injection
│   │       └── exception_handlers.py# Error handling
│   │
│   └── infrastructure/              # 🏗️ Detalles de implementación
│       ├── config/                  # Settings (Pydantic)
│       ├── persistence/             # SQLAlchemy models & repos
│       └── security/                # JWT & password hashing
│
├── scripts/                         # 🛠️ Utilidades
│   └── seed_db.py                   # Poblar BD con datos de prueba
│
├── tests/                           # 🧪 Tests
│   ├── unit/                        # Tests unitarios
│   ├── integration/                 # Tests de integración
│   └── fixtures/                    # Datos de prueba
│
├── requirements.txt                 # 📦 Dependencias Python
├── .env.example                     # 🔐 Template variables entorno
├── Dockerfile                       # 🐳 Containerización
├── docker-compose.yml               # 🐳 Orquestación servicios
├── Saludya_API.postman_collection.json  # 📮 Colección Postman
├── DOCUMENTACION_TECNICA.md         # 📚 Docs técnicas detalladas
├── GUIA_VISUAL_FLUJOS.md            # 🎨 Guía visual de flujos
└── README.md                        # 📖 Este archivo
```

---

## 🔐 Autenticación

### JWT (JSON Web Token)

**Flujo de Autenticación:**

1. **Login**: `POST /auth/login` con email/password
2. **Validación**: Verifica credenciales en BD
3. **Token**: Genera JWT con `sub` (user_id) y `role`
4. **Uso**: Incluir `Authorization: Bearer {token}` en headers
5. **Expiración**: 60 minutos por defecto

**Ejemplo Request:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@example.com", "password": "Pass123!"}'
```

**Ejemplo Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Roles y Permisos

| Endpoint | Admin | Doctor | Patient |
|----------|-------|--------|---------|
| `POST /doctors` | ✅ | ❌ | ❌ |
| `GET /doctors` | ✅ | ✅ | ✅ |
| `POST /appointments` | ✅ | ❌ | ✅ |
| `PATCH /appointments/{id}/confirm` | ✅ | ✅ | ❌ |

---

## 📡 Endpoints Principales

### Autenticación

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123!"
}
```

### Médicos

```http
# Listar médicos
GET /api/v1/doctors?skip=0&limit=20

# Crear médico (Admin)
POST /api/v1/doctors
Authorization: Bearer {admin_token}

{
  "email": "doctor@clinic.com",
  "password": "Pass123!",
  "first_name": "Juan",
  "last_name": "Pérez",
  "specialty": "Cardiología",
  "license_number": "LIC123456",
  "phone": "+34600000001",
  "consultation_duration": 30
}
```

### Pacientes

```http
# Registrar paciente
POST /api/v1/patients

{
  "email": "patient@example.com",
  "password": "Pass123!",
  "first_name": "María",
  "last_name": "García",
  "birth_date": "1990-01-15",
  "phone": "+34600000002",
  "document_number": "12345678A",
  "document_type": "DNI",
  "gender": "F",
  "address": "Calle Principal 123"
}
```

### Citas

```http
# Agendar cita
POST /api/v1/appointments
Authorization: Bearer {token}

{
  "patient_id": "uuid-patient",
  "doctor_id": "uuid-doctor",
  "scheduled_at": "2026-04-15T10:00:00",
  "duration_minutes": 30,
  "notes": "Revisión general"
}

# Confirmar cita (Doctor/Admin)
PATCH /api/v1/appointments/{appointment_id}/confirm
Authorization: Bearer {doctor_token}

# Cancelar cita
PATCH /api/v1/appointments/{appointment_id}/cancel
Authorization: Bearer {token}
```

---

## 🗄️ Base de Datos

### Esquema Principal

```sql
-- Usuarios (base para médicos y pacientes)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'PATIENT')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Médicos
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    specialty VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20),
    consultation_duration INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pacientes
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    birth_date DATE NOT NULL,
    document_number VARCHAR(50) UNIQUE NOT NULL,
    document_type VARCHAR(20) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Citas
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    doctor_id UUID REFERENCES doctors(id),
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Disponibilidad de médicos (futuro)
CREATE TABLE doctor_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id UUID REFERENCES doctors(id),
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Índices Recomendados

```sql
-- Para búsquedas rápidas
CREATE INDEX idx_appointments_doctor_scheduled ON appointments(doctor_id, scheduled_at);
CREATE INDEX idx_appointments_patient_scheduled ON appointments(patient_id, scheduled_at);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

---

## 🐳 Docker

### Ejecutar con Docker Compose

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/saludya_db
      - JWT_SECRET_KEY=your-secret-key
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=saludya_db
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 📊 Scripts Útiles

### Poblar Base de Datos

```bash
python scripts/seed_db.py
```

Crea usuarios de prueba:
- **Admin**: admin@example.com / Admin123!
- **Doctor**: doctor@example.com / Password123!
- **Patient**: patient@example.com / Password123!

### Verificar Salud del Sistema

```bash
# Health check básico
curl http://localhost:8000/api/v1/health

# Ver logs
tail -f logs/app.log
```

### Backup de Base de Datos

```bash
# Backup
pg_dump -U postgres -h localhost saludya_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres -h localhost saludya_db < backup_20260407.sql
```

---

## 🤝 Contribución

### Guía para Contribuidores

1. **Fork** el proyecto
2. **Crear branch** para feature: `git checkout -b feature/nueva-funcionalidad`
3. **Commits** descriptivos siguiendo [Conventional Commits](https://conventionalcommits.org/)
4. **Tests** para nueva funcionalidad
5. **Pull Request** con descripción detallada

### Estándares de Código

- **Black** para formato
- **Flake8** para linting
- **MyPy** para type hints
- **Pytest** para testing

```bash
# Formatear código
black app/ tests/

# Verificar linting
flake8 app/ tests/

# Type checking
mypy app/

# Ejecutar tests
pytest
```

### Versionado

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles
- **MINOR**: Nuevas funcionalidades
- **PATCH**: Bug fixes

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/your-username/saludya-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/saludya-api/discussions)
- **Email**: support@saludya.com

---

## 🙏 Agradecimientos

- **FastAPI** por el framework increíble
- **SQLAlchemy** por el ORM robusto
- **Pydantic** por la validación de datos
- **PostgreSQL** por la base de datos confiable

---

**⭐ Si este proyecto te ayuda, ¡dale una estrella en GitHub!**

*Desarrollado con ❤️ para revolucionar la gestión de citas médicas.*
