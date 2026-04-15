# 🔥 GUÍA VISUAL - FLUJOS Y CONCEPTOS DE SALUDYA API

## 1. Ciclo de Vida de un Usuario

```
FASES DEL USUARIO
=================

┌────────────────────────────────────────────────────┐
│ 1. CREACIÓN                                        │
│    └─ Admin crea Doctor: POST /doctors             │
│       └─ Email único                               │
│       └─ Password hasheado con bcrypt              │
│       └─ Role = "DOCTOR"                           │
│    └─ Paciente se registra: POST /patients         │
│       └─ Sin requerimientos admin                  │
│       └─ Email único                               │
│       └─ Role = "PATIENT"                          │
└──────────────────┬─────────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────────┐
│ 2. AUTENTICACIÓN (Login)                           │
│    └─ Usuario envía: email + password              │
│    └─ Sistema busca por email                      │
│    └─ Valida password con bcrypt.verify()          │
│    └─ Genera JWT con sub (user_id) + role + exp    │
│    └─ Cliente recibe token                         │
│    └─ Guarda en localStorage / header              │
└──────────────────┬─────────────────────────────────┘
                   │
                   ├──RP? (Paciente)──────────┐
                   │                           │
┌──────────────────▼──────────┐      ┌──────────▼──────────────────┐
│ 3A. PACIENTE - AGENDAR CITAS  │    │ 3B. DOCTOR - CONFIRMAR CITAS │
│                               │    │                              │
│ ├─ GET /doctors               │    │ ├─ GET /appointments/doctor/ │
│ │  └─ Ver médicos disponibles │    │ │  └─ Ver mis citas          │
│ │                             │    │ │                            │
│ ├─ POST /appointments         │    │ ├─ PATCH /appointments/.../  │
│ │  └─ Crear cita              │    │ │  └─ Confirmar cita         │
│ │  └─ Status = PENDING        │    │ │  └─ Status = CONFIRMED     │
│ │                             │    │                              │
│ ├─ GET /appointments/patient/ │    │ ├─ PATCH /appointments/.../  │
│ │  └─ Ver mis historial       │    │ │  └─ Cancelar cita          │
│ │                             │    │ │  └─ Status = CANCELLED     │
│ │                             │    │                              │
│ └─ PATCH /appointments/.../   │    │ └─ GET /appointments/doctor/ │
│    └─ Cancelar cita           │    │    └─ Ver historial          │
│    └─ Status = CANCELLED      │    │                              │
└────────────────────────────────────┘   └──────────────────────────┘
```

---

## 2. Diagrama de Autenticación (Login)

```
AUTENTICACIÓN - LOGIN FLOW
===========================

CLIENTE                              SERVIDOR
  │                                     │
  ├─ POST /auth/login ────────────────> │
  │  {                                  │
  │    "email": "user@clinic.com",      │
  │    "password": "Pass123!"           │
  │  }                                  │
  │                                     │LD 1. Buscar usuario por email
  │                                     │  SELECT * FROM users WHERE email = X
  │                                     │
  │                                     │─ No existe?
  │                                     │  └─ Throw UserNotFoundError
  │                                     │
  │                                     │─ Existe pero inactivo?
  │                                     │  └─ Throw UserNotActiveError
  │                                     │
  │                                     │─ Existe y activo:
  │                                     │
  │                                     │LD 2. Verificar password
  │                                     │  bcrypt.verify(input, hash)
  │                                     │
  │                                     │─ Password inválido?
  │                                     │  └─ Throw InvalidCredentialsError
  │                                     │
  │                                     │LD 3. Generar JWT
  │                                     │  Create token:
  │                                     │  {
  │                                     │    "sub": "user-123",
  │                                     │    "role": "DOCTOR",
  │                                     │    "exp": now + 60min
  │                                     │  }
  │                                     │  Sign with SECRET_KEY
  │                                     │
  │<─────────── 200 OK ────────────────┤
  │ {                                   │
  │   "access_token": "eyJhbGc...",     │
  │   "token_type": "bearer"            │
  │ }                                   │
  │                                     │
  ├─ Guardar token en localStorage     │
  │                                     │
  ├─ GET /doctors ────────────────────>│
  │   Authorization: Bearer eyJhbGc...  │
  │                                     │LD 4. Validar token en cada request
  │                                     │  jwt.decode(token, SECRET_KEY)
  │                                     │  ├─ Si expirado: 401
  │                                     │  ├─ Si inválido: 401
  │                                     │  └─ Si válido: extraer user_id, role
  │                                     │
  │<────────────── [ Doctors ] ────────┤
```

---

## 3. Flujo de Creación de Cita (Detallado)

```
CREAR CITA - FLUJO COMPLETO
============================

STEP 1: Paciente entra en app
  ├─ Ver lista de doctores: GET /doctors ✓
  └─ Selecciona: Dr. Juan Pérez

STEP 2: Paciente echa cita
  ├─ Selecciona: 2026-04-15 10:00 AM
  ├─ Envia: POST /appointments
  │   {
  │     "patient_id": "p-123",
  │     "doctor_id": "d-456",
  │     "scheduled_at": "2026-04-15T10:00:00",
  │     "duration_minutes": 30,
  │     "notes": "Revisión general"
  │   }
  └─ Token autenticación: Bearer JWT...

STEP 3: ADAPTER LAYER (HTTP)
  ├─ FastAPI recibe request
  ├─ Pydantic valida schema
  │  ├─ ¿patient_id es UUID válido? ✓
  │  ├─ ¿doctor_id es UUID válido? ✓
  │  ├─ ¿scheduled_at es datetime válido? ✓
  │  └─ ¿duration_minutes > 0? ✓
  ├─ Inyecta dependencias:
  │  ├─ session = sesión BD
  │  └─ current_user = payload JWT
  ├─ Convierte → DTO
  └─ Llama CreateAppointmentUseCase.execute()

STEP 4: APPLICATION LAYER (Use Case)
  ├─ CreateAppointmentUseCase.execute(DTO)
  │
  ├─ Valida Doctor existe:
  │  ├─ doctor = await doctor_repo.find_by_id(d-456)
  │  ├─ if not doctor: DoctorNotFound()
  │  └─ if not doctor.is_active: DoctorInactiveError()
  │
  ├─ Valida Paciente existe:
  │  ├─ patient = await patient_repo.find_by_id(p-123)
  │  ├─ if not patient: PatientNotFound()
  │  └─ if not patient.is_active: PatientInactiveError()
  │
  └─ Crea Appointment entity:
     └─ Appointment.create(...)

STEP 5: DOMAIN LAYER (Entity)
  ├─ Appointment.create() valida REGLAS DE NEGOCIO
  │
  ├─ Validación 1: ¿Fecha es futura?
  │  ├─ if scheduled_at <= now(): 
  │  │  └─ FutureScheduledAtRequired()
  │  ├─ Ejemplo: 2026-04-15 future? ✓ OK
  │  └─ Ejemplo: 2026-04-01 (pasado)? ✗ FAIL
  │
  ├─ Validación 2: ¿Horario laboral?
  │  ├─ hora_inicio = 10 (10 AM)
  │  ├─ hora_fin = 10 + (30 min / 60) = 10.5 (10:30 AM)
  │  ├─ if hora_inicio < 08: OutsideBusinessHours()
  │  ├─ if hora_fin > 17: OutsideBusinessHours()
  │  ├─ Ejemplo: 10:00-10:30 entre 08:00-17:00? ✓ OK
  │  └─ Ejemplo: 23:00-00:00? ✗ FAIL
  │
  ├─ Validación 3: ¿No en fin de semana?
  │  ├─ weekday(2026-04-15) = 2 (Wednesday)
  │  ├─ if weekday > 4: (> Friday) WeekendNotAllowed()
  │  ├─ Ejemplo: Miércoles (2)? ✓ OK
  │  └─ Ejemplo: Sábado (5)? ✗ FAIL
  │
  ├─ Si todas las validaciones OK:
  │  └─ Crear: Appointment(
  │       id = uuid4(),
  │       patient_id = "p-123",
  │       doctor_id = "d-456",
  │       scheduled_at = "2026-04-15T10:00",
  │       duration_minutes = 30,
  │       status = AppointmentStatus.PENDING,
  │       notes = "Revisión general"
  │     )
  │
  └─ Retornar a Application

STEP 6: APPLICATION LAYER (Repository)
  ├─ use_case retorna Appointment entity
  └─ Llama: await appointment_repo.save(appointment)

STEP 7: INFRASTRUCTURE LAYER (Repository Implementation)
  ├─ Mapea Appointment → AppointmentModel (SQLAlchemy)
  │  └─ AppointmentModel(
  │       id = "a-789",
  │       patient_id = "p-123",
  │       doctor_id = "d-456",
  │       scheduled_at = datetime(2026, 4, 15, 10, 0),
  │       duration_minutes = 30,
  │       status = "PENDING",
  │       notes = "Revisión general",
  │     )
  │
  ├─ Agrega a sesión: session.add(model)
  │
  ├─ ANTES DE COMMIT, valida CONFLICTOS:
  │  ├─ SELECT * FROM appointments
  │  │  WHERE doctor_id = d-456
  │  │    AND (
  │  │      (scheduled_at < 2026-04-15T10:30)  // Fin de esta cita
  │  │      AND (scheduled_at + duration > 2026-04-15T10:00)  // Inicio de esta
  │  │    )
  │  │    AND status != 'CANCELLED'
  │  │
  │  ├─ Si encuentra cita existente:
  │  │  └─ Rollback transacción
  │  │  └─ Throw AppointmentSlotUnavailable()
  │  │
  │  └─ Si no hay conflictos: OK
  │
  ├─ Comitea transacción: await session.commit()
  │
  ├─ Refresca modelo: await session.refresh(model)
  │  └─ Ahora model.id tiene valor de BD
  │
  └─ Mapea modelo → Appointment entity (con nuevo ID)

STEP 8: Retorna por capas
  ├─ Repository → Application: entity con ID
  ├─ Use Case → Adapter: entity
  └─ Adapter:
     ├─ Mapea entity → AppointmentResponse (Pydantic)
     ├─ Serializa a JSON
     └─ Retorna 201 Created

STEP 9: RESPUESTA AL CLIENTE
  ├─ Status: 201 Created
  ├─ Body:
  │  {
  │    "id": "a-789",
  │    "patient_id": "p-123",
  │    "doctor_id": "d-456",
  │    "scheduled_at": "2026-04-15T10:00:00",
  │    "duration_minutes": 30,
  │    "status": "PENDING",
  │    "notes": "Revisión general",
  │    "created_at": "2026-04-07T14:23:01"
  │  }
  └─ Cliente recibe confirmación ✓

STEP 10: Paciente ve su cita
  ├─ GET /appointments/patient/p-123
  ├─ Respuesta:
  │  [{
  │    "id": "a-789",
  │    "doctor": "Dr. Juan Pérez",
  │    "scheduled_at": "2026-04-15T10:00",
  │    "status": "PENDING"  // Esperando confirmación del doctor
  │  }]
  └─ Paciente espera que doctor confirme

STEP 11: Doctor confirma cita
  ├─ Doctor verifica su agenda por horario
  ├─ PATCH /appointments/a-789/confirm
  ├─ Response:
  │  {
  │    "id": "a-789",
  │    "status": "CONFIRMED"  // ¡Confirmado!
  │  }
  └─ Paciente notificado (en futura integración)
```

---

## 4. Estructura de Carpetas Explicada

```
saludya-api/
│
├── app/                             # Código de la aplicación
│   │
│   ├── domain/                      # ⭐ NÚCLEO DEL NEGOCIO (Pure Business)
│   │   ├── entities/                # Modelos de datos (User, Doctor, Patient, Appointment)
│   │   │   ├── user.py              # Usuario base (abstracto)
│   │   │   ├── doctor.py            # Médico (extiende User)
│   │   │   ├── patient.py           # Paciente (extiende User)
│   │   │   └── appointment.py       # ⭐ CORE - Lógica de citas
│   │   │
│   │   ├── value_objects/           # Objetos que representan valores
│   │   │   ├── email.py             # Email validado
│   │   │   ├── user_role.py         # Enum: ADMIN | DOCTOR | PATIENT
│   │   │   └── appointment_status.py # Enum: PENDING | CONFIRMED | CANCELLED
│   │   │
│   │   └── exceptions/              # Excepciones de negocio
│   │       └── domain_exceptions.py # UserNotFound, SlotUnavailable, etc.
│   │
│   ├── application/                 # 🔌 ORQUESTACIÓN (Use Cases)
│   │   ├── use_cases/               # Cada caso de uso es un archivo
│   │   │   ├── auth/
│   │   │   │   └── login.py         # LoginUseCase
│   │   │   ├── appointment/
│   │   │   │   ├── create_appointment.py
│   │   │   │   ├── confirm_appointment.py
│   │   │   │   ├── cancel_appointment.py
│   │   │   │   └── get_appointment.py
│   │   │   ├── doctor/
│   │   │   │   ├── create_doctor.py
│   │   │   │   └── get_doctor.py
│   │   │   └── patient/
│   │   │       ├── register_patient.py
│   │   │       └── get_patient.py
│   │   │
│   │   ├── dtos/                    # Data Transfer Objects
│   │   │   ├── auth_dto.py          # LoginDTO, TokenDTO
│   │   │   ├── appointment_dto.py   # CreateAppointmentDTO, AppointmentDTO
│   │   │   ├── doctor_dto.py        # CreateDoctorDTO, DoctorDTO
│   │   │   └── patient_dto.py       # RegisterPatientDTO, PatientDTO
│   │   │
│   │   └── ports/                   # Interfaces (Dependency Inversion)
│   │       ├── input/               # Servicios de entrada
│   │       │   ├── i_auth_service.py
│   │       │   └── i_appointment_service.py
│   │       └── output/              # Repositorios (salida a BD)
│   │           ├── i_appointment_repository.py
│   │           ├── i_doctor_repository.py
│   │           ├── i_patient_repository.py
│   │           └── i_user_repository.py
│   │
│   ├── adapters/                    # 📡 CONEXIONES EXTERNAS (HTTP)
│   │   └── http/
│   │       ├── routes/              # Endpoints FastAPI
│   │       │   ├── auth_routes.py   # POST /auth/login
│   │       │   ├── doctors_routes.py# POST/GET /doctors
│   │       │   ├── patients_routes.py# POST/GET /patients
│   │       │   └── appointments_routes.py # POST/PATCH/GET /appointments
│   │       │
│   │       ├── schemas/             # Pydantic schemas (validación HTTP)
│   │       │   ├── auth_schema.py   # LoginRequest, TokenResponse
│   │       │   ├── doctor_schema.py # CreateDoctorRequest, DoctorResponse
│   │       │   ├── patient_schema.py# RegisterPatientRequest, PatientResponse
│   │       │   └── appointment_schema.py # CreateAppointmentRequest
│   │       │
│   │       ├── dependencies.py      # Inyección: auth, BD, etc.
│   │       │                        # Aquí está: get_current_user, require_admin
│   │       │
│   │       └── exception_handlers.py# Convertir excepciones → HTTP
│   │                                # UserNotFound → 404 JSON
│   │
│   └── infrastructure/              # 🔧 DETALLES DE IMPLEMENTACIÓN
│       ├── config/
│       │   └── settings.py          # Configuración vía .env
│       │
│       ├── persistence/             # Base de Datos
│       │   ├── database.py          # Conexión, sesión
│       │   │
│       │   ├── models/              # Modelos SQLAlchemy (ORM)
│       │   │   ├── user_model.py
│       │   │   ├── doctor_model.py
│       │   │   ├── patient_model.py
│       │   │   └── appointment_model.py
│       │   │
│       │   └── repositories/        # Implementación de puertos
│       │       ├── user_repository_impl.py     # Implementa IUserRepository
│       │       ├── doctor_repository_impl.py   # Implementa IDoctorRepository
│       │       ├── patient_repository_impl.py  # Implementa IPatientRepository
│       │       └── appointment_repository_impl.py # Implementa IAppointmentRepository
│       │
│       └── security/                # Autenticación
│           ├── jwt_handler.py       # Generar/validar JWT
│           └── password_hasher.py   # Hash/verify con bcrypt
│
├── scripts/
│   └── seed_db.py                   # Llenar BD con datos de prueba
│
├── tests/                           # Pruebas unitarias e integración
│
├── requirements.txt                 # Dependencias pip
├── .env                             # Secretos (NO en git)
├── .gitignore
├── Dockerfile                       # Containerización
└── README.md
```

---

## 5. Cómo los Datos Fluyen: Ejemplo Real

```
SCENARIO: Paciente María agenda cita con Dr. Juan
=====================================================

CLIENT (Frontend)
═════════════════
User selecciona:
  - Doctor: Juan Pérez
  - Date: 2026-04-15
  - Time: 10:00 AM
  - Duration: 30 min

María hace click en "Confirmar"
  ↓ POST /appointments
  ├─ Authorization: Bearer eyJhbGc_eyJ... (María's token)
  └─ Body:
     {
       "patient_id": "550e8400-e29b-...", (María)
       "doctor_id": "660f9511-f40c-...", (Juan)
       "scheduled_at": "2026-04-15T10:00:00",
       "duration_minutes": 30,
       "notes": ""
     }


ADAPTER LAYER (HTTP → DTO)
═══════════════════════════
FastAPI @router.post("/appointments")
  │
  ├─ Pydantic recibe JSON
  ├─ Valida tipos (UUID, datetime, int)
  │
  ├─ Extrae dependencias:
  │  ├─ session = get_db_session() → Sesión asyncio BD
  │  └─ _current_user = get_current_user() → {"user_id": "...", "role": "PATIENT"}
  │
  ├─ Convierte a DTO:
     └─ CreateAppointmentDTO(
          patient_id="550e8400-...",
          doctor_id="660f9511-...",
          scheduled_at=datetime(2026, 4, 15, 10, 0),
          duration_minutes=30,
          notes=""
        )
  │
  └─ Ejecuta: use_case.execute(dto)


APPLICATION LAYER (Orquestación)
═════════════════════════════════
CreateAppointmentUseCase.execute(DTO)
  │
  ├─ Busca doctor en BD:
  │  └─ doctor = await doctor_repo.find_by_id("660f9511-...")
  │     ├─ Query: SELECT * FROM doctors WHERE id = ...
  │     ├─ Resultado: Doctor {
  │     │   id: "660f9511-...",
  │     │   user_id: "770g0622-...",
  │     │   specialty: "Cardiología",
  │     │   license_number: "LIC123456",
  │     │   consultation_duration: 30,
  │     │   availability: [...]
  │     │ }
  │     └─ Si no existe: raise DoctorNotFound()
  │
  ├─ Busca paciente en BD:
  │  └─ patient = await patient_repo.find_by_id("550e8400-...")
  │     ├─ Query: SELECT * FROM patients WHERE id = ...
  │     ├─ Resultado: Patient {
  │     │   id: "550e8400-...",
  │     │   user_id: "880h1733-...",
  │     │   first_name: "María",
  │     │   last_name: "García",
  │     │   birth_date: "1990-01-15",
  │     │   ...
  │     │ }
  │     └─ Si no existe: raise PatientNotFound()
  │
  └─ Crea Appointment en dominio:
     └─ appointment = Appointment.create(...)


DOMAIN LAYER (Validaciones de Negocio)
═══════════════════════════════════════
Appointment.create() valida REGLAS:

[1] ¿Fecha es futura?
    ├─ now() = 2026-04-07 14:00
    ├─ scheduled_at = 2026-04-15 10:00
    ├─ 2026-04-15 > 2026-04-07? ✓ YES
    └─ Continue...

[2] ¿Horario laboral?
    ├─ hour_start = 10
    ├─ hour_end = 10 + (30 / 60) = 10.5
    ├─ 10 >= 8? ✓ YES
    ├─ 10.5 <= 17? ✓ YES
    └─ Continue...

[3] ¿No es fin de semana?
    ├─ weekday(2026-04-15) = 2 (Wednesday)
    ├─ 2 <= 4 (lunes a viernes)? ✓ YES
    └─ Continue...

[4] ¿Doctor disponible en esa hora?
    ├─ doctor.availability = [
    │   {day: 1, start: 08:00, end: 17:00},
    │   {day: 2, start: 08:00, end: 17:00},
    │   ...
    │  ]
    ├─ ¿Miércoles (2) en availability? ✓ YES
    └─ Continue...

✓ TODAS LAS VALIDACIONES PASARON
  └─ Crear entidad:
     Appointment {
       id: UUID(uuid4()),
       patient_id: "550e8400-...",
       doctor_id: "660f9511-...",
       scheduled_at: datetime(2026, 4, 15, 10, 0),
       duration_minutes: 30,
       status: AppointmentStatus.PENDING,
       notes: "",
       created_at: datetime.now()
     }


INFRASTRUCTURE LAYER (BD)
═════════════════════════
appointment_repo.save(appointment):
  │
  ├─ Mapea entidad → Modelo SQLAlchemy:
  │  └─ model = AppointmentModel(
  │       id = appointment.id,
  │       patient_id = appointment.patient_id,
  │       doctor_id = appointment.doctor_id,
  │       scheduled_at = appointment.scheduled_at,
  │       duration_minutes = appointment.duration_minutes,
  │       status = "PENDING",
  │       notes = "",
  │       created_at = appointment.created_at
  │     )
  │
  ├─ VERIFY NO CONFLICT (detección de doble booking):
  │  ├─ SELECT * FROM appointments WHERE
  │  │   doctor_id = '660f9511-...' AND
  │  │   scheduled_at < 2026-04-15T10:30 AND
  │  │   (scheduled_at + interval '30 minutes') > 2026-04-15T10:00 AND
  │  │   status != 'CANCELLED'
  │  │
  │  ├─ ¿Hay overlaps? NO
  │  └─ Continue...
  │
  ├─ session.add(model)  # Agrega a transacción
  ├─ await session.commit()  # Escribe a BD
  │  ├─ INSERT INTO appointments (...) VALUES (...)
  │  ├─ RETURNING id  # BD genera ID si falta
  │  └─ Transaction OK
  │
  ├─ await session.refresh(model)
  │  └─ Refresca modelo con valores de BD (ID confirmado)
  │
  └─ Mapea modelo → Entidad:
     └─ Retorna: appointment (con ID confirmado)


BACK TO ADAPTER LAYER (DTO → JSON)
═══════════════════════════════════
Convierte entidad → Response Schema:
  │
  └─ AppointmentResponse(
       id="UUID...",
       patient_id="550e8400-...",
       doctor_id="660f9511-...",
       scheduled_at="2026-04-15T10:00:00",
       duration_minutes=30,
       status="PENDING",
       notes="",
       created_at="2026-04-07T14:00:00"
     )


CLIENT RESPONSE
═══════════════
Status Code: 201 Created
Content-Type: application/json

{
  "id": "aaaaaa00-bbbb-cccc-dddd-eeeeeeeeeeee",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "doctor_id": "660f9511-f40c-52e5-b827-557766551111",
  "scheduled_at": "2026-04-15T10:00:00",
  "duration_minutes": 30,
  "status": "PENDING",
  "notes": "",
  "created_at": "2026-04-07T14:23:01"
}

✓ CITA AGENDADA EXITOSAMENTE
  └─ María ve notification: "Cita agendada. Esperando confirmación del doctor."
```

---

## 6. Matriz de Permisos y Roles

```
MATRIZ DE SEGURIDAD
═══════════════════

                           │ ADMIN │ DOCTOR │ PATIENT │
───────────────────────────┼───────┼────────┼─────────┤
POST   /doctors (crear)     │  ✓✓✓  │   ✗    │   ✗    │
GET    /doctors (listar)    │  ✓✓✓  │  ✓✓    │   ✓    │
GET    /doctors/{id}        │  ✓✓✓  │  ✓✓    │   ✓    │
───────────────────────────┼───────┼────────┼─────────┤
POST   /patients (registrar)│ (auto)│   ✗    │  ✓(auto)│
GET    /patients (listar)   │  ✓✓✓  │   ✗    │   ✗    │
GET    /patients/{id}       │  ✓✓✓  │   ✗    │  ✓(own) │
───────────────────────────┼───────┼────────┼─────────┤
POST   /appointments        │  ✓✓✓  │   ✗    │  ✓(own) │
GET    /appointments        │  ✓✓✓  │  ✓✓    │   ✗    │
GET    /appointments/{id}   │  ✓✓✓  │  ✓(own)│  ✓(own) │
GET    /appointments/p/{id} │  ✓✓✓  │   ✗    │  ✓(own) │
GET    /appointments/d/{id} │  ✓✓✓  │  ✓(own)│   ✗    │
───────────────────────────┼───────┼────────┼─────────┤
PATCH  /appointments/{}/confirm │  ✓✓✓  │  ✓✓    │   ✗   │
PATCH  /appointments/{}/cancel  │  ✓✓✓  │  ✓(own)│  ✓(own)│
───────────────────────────┼───────┼────────┼─────────┤

Significado:
  ✓    = Permitido
  ✗    = Prohibido (401 Unauthorized o 403 Forbidden)
  (own) = Solo sus propios registros
  (auto)= Se asigna automáticamente del JWT
```

---

## 7. Posibles Errores y Cómo se Manejan

```
ERROR HANDLING FLOW
═══════════════════

┌─ REQUEST: POST /appointments
│
├─ ADAPTER VALIDA
│  ├─ ❌ JSON inválido
│  │  └─ 400 Bad Request: "Invalid JSON"
│  │
│  ├─ ❌ Campo falta
│  │  └─ 422 Unprocessable Entity: "Field required"
│  │
│  └─ ✓ JSON válido
│
├─ AUTH VALIDA
│  ├─ ❌ Sin token
│  │  └─ 401 Unauthorized: "Missing token"
│  │
│  ├─ ❌ Token expirado
│  │  └─ 401 Unauthorized: "Token expired"
│  │
│  ├─ ❌ Token inválido
│  │  └─ 401 Unauthorized: "Invalid token"
│  │
│  └─ ✓ Token válido
│
├─ USE CASE VALIDA
│  ├─ ❌ Doctor no existe
│  │  └─ 404 Not Found: "Doctor not found"
│  │
│  ├─ ❌ Paciente no existe
│  │  └─ 404 Not Found: "Patient not found"
│  │
│  └─ ✓ Ambos existen
│
├─ DOMINIO VALIDA
│  ├─ ❌ Fecha en pasado
│  │  └─ 400 Bad Request: "Appointment must be in future"
│  │
│  ├─ ❌ Horario fuera laboral
│  │  └─ 400 Bad Request: "Outside business hours (8-17)"
│  │
│  ├─ ❌ Fin de semana
│  │  └─ 400 Bad Request: "Weekends not allowed"
│  │
│  ├─ ❌ Slot ocupado
│  │  └─ 409 Conflict: "Slot unavailable"
│  │
│  └─ ✓ Todas validaciones OK
│
├─ INFRAESTRUCTURA VALIDA
│  ├─ ❌ Error en BD
│  │  └─ 500 Internal Server Error: "Database error"
│  │
│  └─ ✓ INSERT OK
│
└─ ✓ 201 Created + JSON Response

Implementación en código:
───────────────────────────

# exception_handlers.py
@app.exception_handler(DoctorNotFound)
async def handle_doctor_not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Doctor not found"}
    )

@app.exception_handler(AppointmentSlotUnavailable)
async def handle_slot_unavailable(request, exc):
    return JSONResponse(
        status_code=409,
        content={"detail": "Slot unavailable"}
    )
```

---

## 8. Setup y Ejecución

```
DESARROLLO LOCAL
════════════════

1. SETUP INICIAL
   ├─ Python 3.10+
   ├─ PostgreSQL running
   ├─ pip install -r requirements.txt
   ├─ .env con:
   │  ├─ DATABASE_URL=postgresql+asyncpg://...
   │  ├─ JWT_SECRET_KEY=your-secret
   │  └─ JWT_EXPIRE_MINUTES=60
   └─ scripts/seed_db.py para datos iniciales

2. LEVANTAR SERVIDOR
   ├─ uvicorn app.main:app --reload --port 8000
   └─ http://localhost:8000/docs (Swagger UI)

3. TESTEAR
   ├─ Postman collection (Saludya_API.postman_collection.json)
   └─ O con curl:
      curl -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"user@example.com","password":"Pass123!"}'

4. ENDPOINTS PRINCIPALES
   ├─ POST /api/v1/auth/login
   ├─ POST /api/v1/doctors (admin)
   ├─ GET  /api/v1/doctors
   ├─ POST /api/v1/patients
   ├─ GET  /api/v1/patients (admin)
   ├─ POST /api/v1/appointments
   ├─ GET  /api/v1/appointments (admin/doctor)
   ├─ PATCH /api/v1/appointments/{id}/confirm
   └─ PATCH /api/v1/appointments/{id}/cancel
```

---

## Resumen Visual Final

```
LAYERS SUMMARY
══════════════

┌──────────────────────────────────────────────────┐
│ HTTP REQUEST                                     │
│ POST /appointments {"patient_id": "...", ...}    │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│ ADAPTER (HTTP) - @ routes/appointments_routes.py │
│ ├─ Pydantic validate schema                      │
│ ├─ Extract dependencies (auth, DB)               │
│ ├─ Convert to DTO                                │
│ └─ Call use_case.execute(DTO)                    │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│ APPLICATION (Use Case) - @ use_cases/...         │
│ ├─ Validate doctor exists                        │
│ ├─ Validate patient exists                       │
│ ├─ Call Appointment.create() with validation     │
│ ├─ Persist via repository                        │
│ └─ Return entity to adapter                      │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│ DOMAIN (Entity) - @ domain/entities/appointment  │
│ ├─ PURE BUSINESS LOGIC - No framework deps       │
│ ├─ Validate future date                          │
│ ├─ Validate business hours                       │
│ ├─ Validate not weekend                          │
│ ├─ Validate doctor availability                  │
│ ├─ Create entity if all OK                       │
│ └─ Raise exceptions if invalid                   │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│ INFRASTRUCTURE (Repository) - @ persistence/..   │
│ ├─ Map entity → SQLAlchemy model                 │
│ ├─ Query DB for conflicts                        │
│ ├─ INSERT/UPDATE in transaction                  │
│ ├─ COMMIT changes                                │
│ ├─ Map model → entity                            │
│ └─ Return to use case                            │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ POSTGRESQL DB │
         └───────────────┘
                 │
                 ▼ (Datos persistidos)
                 │
        RETORNO (Flujo inverso)
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│ ADAPTER (Response)                               │
│ ├─ Map entity → Response schema                  │
│ ├─ Serialize to JSON                             │
│ ├─ Set status code 201 Created                   │
│ └─ Return to client                              │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│ HTTP RESPONSE 201 Created                        │
│ {                                                │
│   "id": "...",                                   │
│   "status": "PENDING",                           │
│   ...                                            │
│ }                                                │
└──────────────────────────────────────────────────┘
```

---

**Este documento es una guía visual para entender cómo fluyen los datos y las validaciones a través de la arquitectura Clean Architecture de Saludya API.**

Para preguntas específicas, revisar **DOCUMENTACION_TECNICA.md** para más detalles.
