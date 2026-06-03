# Manual Tecnico

## Estructura de carpetas

```text
saludya-api/
├── app/
│   ├── adapters/
│   │   └── http/
│   │       ├── routes/
│   │       ├── schemas/
│   │       ├── dependencies.py
│   │       └── exception_handlers.py
│   ├── application/
│   │   ├── dtos/
│   │   ├── ports/
│   │   └── use_cases/
│   ├── domain/
│   │   ├── entities/
│   │   ├── exceptions/
│   │   └── value_objects/
│   ├── infrastructure/
│   │   ├── config/
│   │   ├── persistence/
│   │   └── security/
│   └── main.py
├── scripts/
│   └── seed_db.py
├── requirements.txt
├── Dockerfile
└── docs/
```

## Tecnologias

- Python 3.11.
- FastAPI.
- Uvicorn.
- SQLAlchemy async.
- PostgreSQL mediante asyncpg.
- Pydantic y pydantic-settings.
- python-jose para JWT.
- passlib/bcrypt para hash de contrasenas.

## Variables de entorno

| Variable | Requerida | Valor por defecto | Descripcion |
| --- | --- | --- | --- |
| `DATABASE_URL` | Si | Ninguno | Cadena de conexion async a PostgreSQL. |
| `DB_ECHO` | No | `False` | Habilita logging SQL. |
| `JWT_SECRET_KEY` | Si | Ninguno | Clave usada para firmar JWT. |
| `JWT_ALGORITHM` | No | `HS256` | Algoritmo de firma JWT. |
| `JWT_EXPIRE_MINUTES` | No | `60` | Duracion del token. |
| `APP_NAME` | No | `Health Appointments API` | Nombre mostrado por FastAPI. |
| `APP_VERSION` | No | `0.1.0` | Version del sistema. |
| `DEBUG` | No | `False` | Controla CORS abierto o restringido. |

Ejemplo `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/saludya_db
DB_ECHO=False
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
APP_NAME=Saludya API
APP_VERSION=0.1.0
DEBUG=True
```

## Dependencias

Las dependencias se instalan desde:

```bash
pip install -r requirements.txt
```

Dependencias principales observadas:

```text
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
pydantic[email]
pydantic-settings
passlib[bcrypt]
python-jose[cryptography]
bcrypt
python-dotenv
```

## Configuracion local

1. Crear entorno virtual:

```bash
python -m venv venv
```

2. Activar entorno en Windows:

```bash
venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear archivo `.env` en la raiz con las variables requeridas.

5. Asegurar que PostgreSQL este disponible y que `DATABASE_URL` apunte a una base existente.

## Comandos de ejecucion

Ejecutar servidor local:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abrir documentacion:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

Health check:

```bash
curl http://localhost:8000/health
```

## Endpoints documentados

| Metodo | Ruta | Autenticacion | Request | Response | Errores posibles |
| --- | --- | --- | --- | --- | --- |
| GET | `/health` | No | No aplica | `status`, `version` | Error de disponibilidad del servidor |
| POST | `/api/v1/auth/login` | No | `LoginRequest` | `TokenResponse` | 401 credenciales invalidas o usuario inactivo, 422 datos invalidos |
| POST | `/api/v1/patients` | No | `RegisterPatientRequest` | `PatientResponse` | 409 email/documento duplicado, 422 datos invalidos |
| GET | `/api/v1/patients` | Admin | Query `skip`, `limit` | Lista `PatientResponse` | 401 token invalido, 403 rol insuficiente |
| GET | `/api/v1/patients/{patient_id}` | Usuario autenticado | Path UUID | `PatientResponse` | 401 token invalido, 404 no encontrado, 422 UUID invalido |
| POST | `/api/v1/doctors` | Admin | `CreateDoctorRequest` | `DoctorResponse` | 401, 403, 409/422 segun conflicto o validacion |
| GET | `/api/v1/doctors` | Usuario autenticado | Query `skip`, `limit` | Lista `DoctorResponse` | 401, 422 |
| GET | `/api/v1/doctors/{doctor_id}` | Usuario autenticado | Path UUID | `DoctorResponse` | 401, 404, 422 |
| POST | `/api/v1/appointments` | Usuario autenticado | `CreateAppointmentRequest` | `AppointmentResponse` | 401, 404, 409, 422 |
| PATCH | `/api/v1/appointments/{appointment_id}/confirm` | Admin o doctor | Path UUID | `AppointmentResponse` | 401, 403, 404, 422 |
| PATCH | `/api/v1/appointments/{appointment_id}/cancel` | Usuario autenticado | Path UUID | `AppointmentResponse` | 401, 404, 422 |
| GET | `/api/v1/appointments/patient/{patient_id}` | Usuario autenticado | Path UUID, query | Lista `AppointmentResponse` | 401, 422 |
| GET | `/api/v1/appointments/doctor/{doctor_id}` | Admin o doctor | Path UUID, query | Lista `AppointmentResponse` | 401, 403, 422 |
| GET | `/api/v1/appointments` | Admin o doctor | Query `status`, `skip`, `limit` | `AppointmentListResponse` | 401, 403, 422 |
| GET | `/api/v1/appointments/{appointment_id}` | Usuario autenticado | Path UUID | `AppointmentResponse` | 401, 404, 422 |

## Modelos de base de datos

### users

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | UUID | PK, default uuid4 |
| `email` | String(255) | Unico, no nulo, index |
| `password_hash` | String(255) | No nulo |
| `role` | String(20) | No nulo |
| `is_active` | Boolean | No nulo, default true |
| `created_at` | DateTime timezone | No nulo |
| `updated_at` | DateTime timezone | No nulo |

### patients

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK `users.id`, unico, no nulo, index |
| `first_name` | String(100) | No nulo |
| `last_name` | String(100) | No nulo |
| `birth_date` | Date | Opcional |
| `phone` | String(20) | Opcional |
| `document_number` | String(30) | Unico, opcional, index |
| `document_type` | String(20) | Opcional |
| `gender` | String(10) | Opcional |
| `address` | Text | Opcional |
| `created_at` | DateTime timezone | No nulo |

### doctors

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK `users.id`, unico, no nulo, index |
| `first_name` | String(100) | No nulo |
| `last_name` | String(100) | No nulo |
| `specialty` | String(100) | No nulo |
| `license_number` | String(50) | Unico, no nulo, index |
| `phone` | String(20) | Opcional |
| `consultation_duration` | Integer | No nulo, default 30 |
| `created_at` | DateTime timezone | No nulo |

### doctor_availability

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | UUID | PK |
| `doctor_id` | UUID | FK `doctors.id`, no nulo, index |
| `day_of_week` | SmallInteger | No nulo; 1 lunes a 5 viernes segun comentario |
| `start_time` | Time | No nulo |
| `end_time` | Time | No nulo |
| `is_active` | Boolean | No nulo, default true |

### appointments

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | UUID | PK |
| `patient_id` | UUID | FK `patients.id`, no nulo, index |
| `doctor_id` | UUID | FK `doctors.id`, no nulo, index |
| `scheduled_at` | DateTime timezone | No nulo, index |
| `duration_minutes` | Integer | No nulo, default 30 |
| `status` | Enum `appointment_status` | No nulo, default pending, index |
| `notes` | Text | Opcional |
| `created_at` | DateTime timezone | No nulo |
| `updated_at` | DateTime timezone | No nulo |

## Observaciones tecnicas

- El repositorio no contiene migraciones Alembic.
- El `Dockerfile` existe pero esta vacio.
- Existen archivos de casos de uso no conectados directamente por rutas actuales, como algunos flujos alternos de confirmacion/cancelacion/reprogramacion. La API activa usa `update_appointment_status.py` para confirmar y cancelar.
- Hay impresiones `print` de depuracion en login y database que conviene retirar o reemplazar por logging formal antes de produccion.

