# 📋 DOCUMENTACIÓN TÉCNICA Y LÓGICA - SALUDYA API

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Visión General del Proyecto](#visión-general-del-proyecto)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Flujo de Datos](#flujo-de-datos)
5. [Modelos de Datos](#modelos-de-datos)
6. [Casos de Uso Principales](#casos-de-uso-principales)
7. [Autenticación y Autorización](#autenticación-y-autorización)
8. [API Endpoints](#api-endpoints)
9. [Patrones de Diseño](#patrones-de-diseño)
10. [Cómo Funciona Cada Componente](#cómo-funciona-cada-componente)

---

## Introducción

**Saludya API** es una plataforma backend para gestión de citas médicas. Permite que pacientes agenden citas con médicos, que médicos administren sus horarios, y que administradores supervisen todo el sistema.

**Objetivo:** Proporcionar un sistema confiable, escalable y mantenible para coordinar servicios de salud.

**Stack Tecnológico:**
- **Backend:** Python 3.10+
- **Framework:** FastAPI (async, alto rendimiento)
- **Base de Datos:** PostgreSQL (vía SQLAlchemy async)
- **Autenticación:** JWT (JSON Web Tokens)
- **Seguridad:** bcrypt (password hashing)
- **Servidor:** Uvicorn (ASGI)

---

## Visión General del Proyecto

### ¿Qué problem resuelve?

En una clínica u hospital tradicional:
- Pacientes llaman para agendar citas ❌ Tedioso
- Médicos tienen agendas en papel ❌ Poco confiable
- No hay control de disponibilidad ❌ Doble booking
- Difícil de escalar ❌ Necesita más personal

**Saludya resuelve esto:**
- ✅ Agendamiento online de citas
- ✅ Control de disponibilidad en tiempo real
- ✅ Historial digital de citas
- ✅ Roles y permisos claros
- ✅ Escalable y automatizado

### Actores del Sistema

1. **Administrador (Admin)**: Controla médicos, pacientes y citas. Acceso total.
2. **Médico (Doctor)**: Ve su agenda, confirma/cancela citas. Solo sus propias citas.
3. **Paciente (Patient)**: Agenda citas, ve sus propias citas histórico.
4. **Sistema**: Valida reglas, genera tokens, persiste datos.

---

## Arquitectura del Sistema

### Modelo de Capas (Clean Architecture)

```
┌─────────────────────────────────────────┐
│   ADAPTERS LAYER (HTTP)                 │
│   - Routers (endpoints)                 │
│   - Schemas (Pydantic)                  │
│   - Exception Handlers                  │
└──────────────┬──────────────────────────┘
               │ (Dependency Injection)
┌──────────────▼──────────────────────────┐
│   APPLICATION LAYER                     │
│   - Use Cases (lógica de aplicación)    │
│   - DTOs (data transfer objects)        │
│   - Ports (interfaces)                  │
└──────────────┬──────────────────────────┘
               │ (Dependency Inversion)
┌──────────────▼──────────────────────────┐
│   DOMAIN LAYER                          │
│   - Entities (puro negocio)             │
│   - Value Objects                       │
│   - Domain Exceptions                   │
└──────────────┬──────────────────────────┘
               │ (Implementación concreta)
┌──────────────▼──────────────────────────┐
│   INFRASTRUCTURE LAYER                  │
│   - Repositories (+SQL)                 │
│   - JWT Handler                         │
│   - Password Hasher                     │
│   - Database Configuration              │
└─────────────────────────────────────────┘
```

### ¿Por qué esta estructura?

**Ventajas:**
- 🔄 **Independencia de Tecnología:** Cambiar BD o auth sin afectar lógica de negocio
- 🧪 **Testeable:** Mockeamos repos, no necesitamos BD real
- 📦 **Mantenible:** Cada capa tiene responsabilidad clara
- 🚀 **Escalable:** Agregar features sin modificar código existente
- 🛡️ **Seguro:** Validaciones en múltiples capas

---

## Flujo de Datos

### Flujo de una Solicitud HTTP Típica

```
1. REQUEST
   ├─ Cliente envía: POST /api/v1/appointments
   └─ Payload: { patient_id, doctor_id, scheduled_at }

2. ADAPTER LAYER (HTTP)
   ├─ FastAPI recibe request
   ├─ Pydantic valida schema (CreateAppointmentRequest)
   ├─ Dependencia inyecta sesión DB y usuario autenticado
   └─ Convierte schema → DTO

3. APPLICATION LAYER
   ├─ Use Case: CreateAppointmentUseCase.execute(DTO)
   ├─ Recupera Paciente y Médico desde repositorio
   └─ Crea entidad Appointment (dominio)

4. DOMAIN LAYER
   ├─ Appointment.create() valida:
   │  ├─ ¿Paciente existe?
   │  ├─ ¿Médico existe?
   │  ├─ ¿Slot disponible?
   │  ├─ ¿Fecha es futura?
   │  └─ ¿Horario laboral (08:00-17:00)?
   └─ Si falla → lanza excepción de dominio

5. INFRASTRUCTURE LAYER
   ├─ Repository recibe entidad
   ├─ Mapea a modelo SQLAlchemy
   ├─ Ejecuta: INSERT INTO appointments ...
   └─ Retorna entidad con ID generado

6. APPLICATION LAYER
   └─ Retorna entidad al adaptador

7. ADAPTER LAYER
   ├─ Convierte entidad → AppointmentResponse (schema)
   └─ Serializa a JSON

8. RESPONSE
   ├─ StatusCode: 201 (Created)
   └─ Body: { id, patient_id, doctor_id, status: "PENDING", ... }
```

### Error Handling

```
Si exception en DOMAIN:
  ├─ Lanza: AppointmentSlotUnavailableException
  └─ Propagada a APPLICATION
     └─ Propagada a ADAPTER
        └─ Exception Handler convierte a:
           ├─ HTTP 400/409
           └─ {"detail": "Slot no disponible"}
```

---

## Modelos de Datos

### 1. User (Base - DOMAIN)

```python
class User:
    id: UUID
    email: str              # Único
    password_hash: str      # bcrypt
    first_name: str
    last_name: str
    role: UserRole          # ADMIN | DOCTOR | PATIENT
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**Lógica:** 
- Entidad base para todos los usuarios
- El rol determina permisos en la API
- Password nunca se almacena en texto plano

---

### 2. Doctor (DOMAIN)

```python
class Doctor(User):
    specialty: str          # "Cardiología", "Pediatría", etc.
    license_number: str     # Cédula profesional
    phone: str
    consultation_duration: int  # Minutos (ej: 30)
    availability: List[DoctorAvailability]  # Horarios
```

**Lógica:**
- Hereda de User (role = DOCTOR)
- `specialty` ayuda a pacientes a encontrar médicos
- `availability` define horarios de atención (ej: Lunes 08:00-17:00)

---

### 3. Patient (DOMAIN)

```python
class Patient(User):
    birth_date: date
    document_number: str    # Cédula/DNI
    document_type: str      # "DNI", "CEDULA", etc.
    gender: str             # "M", "F"
    address: str
```

**Lógica:**
- Hereda de User (role = PATIENT)
- Información médica básica
- Permite traceo de identidad

---

### 4. Appointment (DOMAIN) - **Core del Negocio**

```python
class Appointment:
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime      # Cuándo es la cita
    duration_minutes: int       # Cuánto dura (ej: 30)
    status: AppointmentStatus   # PENDING | CONFIRMED | CANCELLED
    notes: str                  # "Revisión general"
    created_at: datetime
    updated_at: datetime
```

**Estados (Value Object):**
```
PENDING ────────► CONFIRMED ─────┐
  ▲                               ├──► CANCELLED
  └─ desde cualquier estado ──────┘
```

**Validaciones (Lógica de Dominio):**
1. ✅ Paciente y Médico existen
2. ✅ Slot no está ocupado (no 2 citas en mismo horario)
3. ✅ Cita no es en el pasado
4. ✅ Horario está dentro disponibilidad del médico (08:00-17:00, lun-vie)
5. ✅ Duración respeta configuración del médico

---

### 5. Value Objects (DOMAIN)

```python
class Email(ValueObject):
    """Email validado"""
    value: str
    # Valida formato email en constructor
    
class UserRole(ValueObject):
    """Rol de usuario"""
    # ADMIN | DOCTOR | PATIENT
    
class AppointmentStatus(ValueObject):
    """Estado de cita"""
    # PENDING | CONFIRMED | CANCELLED
```

---

## Casos de Uso Principales

### UC1: Login (Autenticación)

**Actores:** Usuario (cualquier rol)

**Flujo:**
```
1. Usuario envía: email + password
2. Use Case: LoginUseCase.execute(LoginDTO)
   ├─ Busca usuario por email en BD
   ├─ Si NO existe → UserNotFoundError
   ├─ Si existe pero inactivo → UserNotActiveError
   ├─ Valida password con bcrypt.verify()
   ├─ Si password inválido → InvalidCredentialsError
   ├─ Si válido → Genera JWT con:
   │  ├─ sub: user_id (subject)
   │  ├─ role: user.role
   │  └─ exp: ahora + 60 minutos
   └─ Retorna: { access_token, token_type: "bearer" }
3. Cliente guarda token en header Authorization
```

**Seguridad:**
- Password NUNCA viajando en texto plano
- JWT expira en 60 min (cambiar en .env)
- bcrypt tiene salt, imposible rainbow tables

---

### UC2: Agendar Cita (Main Business Logic)

**Actores:** Paciente (autenticado)

**Precondiciones:**
- Usuario autenticado
- Tiene rol PATIENT (o el sistema asocia automáticamente)

**Flujo:**
```
1. Paciente envía:
   ├─ patient_id (su ID)
   ├─ doctor_id (doctor elegido)
   ├─ scheduled_at (2026-04-15 10:00)
   ├─ duration_minutes (30)
   └─ notes ("revisión anual")

2. CreateAppointmentUseCase.execute(CreateAppointmentDTO)
   ├─ Valida doctor existe y está activo
   ├─ Valida paciente existe y está activo
   ├─ Verifica horario laboral del médico:
   │  ├─ ¿Es Monday-Friday? (no weekends)
   │  ├─ ¿10:00 >= 08:00? (inicio workday)
   │  └─ ¿10:30 <= 17:00? (fin workday)
   ├─ Verifica 30 min no chocan con otra cita:
   │  └─ SELECT * FROM appointments
   │     WHERE doctor_id = X AND scheduled_at overlaps
   ├─ Crea entidad: Appointment(status=PENDING)
   ├─ Guarda en BD
   └─ Retorna appointment con id generado

3. Respuesta: 201 Created + AppointmentResponse
```

**Transacciones:**
- TODO debe ser atómico: doctor valido → slot libre → INSERT
- Si falla, rollback automático en BD

**Errores Posibles:**
```
❌ 400 BadRequest: scheduled_at en pasado
❌ 409 Conflict: Slot ocupado
❌ 422 UnprocessableEntity: Doctor no existe
❌ 403 Forbidden: Sin permisos (no es paciente)
```

---

### UC3: Confirmar Cita

**Actores:** Médico o Admin

**Flujo:**
```
1. Médico envía: PATCH /appointments/{id}/confirm

2. ConfirmAppointmentUseCase.execute(appointment_id)
   ├─ Busca cita
   ├─ Valida status = PENDING (no confirmar 2 veces)
   ├─ Cambia status a CONFIRMED
   ├─ Actualiza updated_at
   └─ Guarda

3. Respuesta: 200 OK + AppointmentResponse con status="CONFIRMED"
```

---

### UC4: Cancelar Cita

**Actores:** Paciente, Médico o Admin

**Flujo:**
```
1. Usuario envía: PATCH /appointments/{id}/cancel

2. CancelAppointmentUseCase.execute(appointment_id)
   ├─ Busca cita
   ├─ Permite cancelar desde cualquier status
   ├─ Cambia status a CANCELLED
   └─ Guarda

3. Respuesta: 200 OK + AppointmentResponse con status="CANCELLED"
```

---

### UC5: Listar Citas de Paciente

**Actores:** Paciente (ve sus propias citas), Admin (ve todas)

**Flujo:**
```
1. Paciente envía: GET /appointments/patient/{patient_id}?skip=0&limit=20

2. GetAppointmentsByPatientUseCase.execute(patient_id, skip, limit)
   ├─ Busca EN BD:
   │  └─ SELECT * FROM appointments
   │     WHERE patient_id = X
   │     LIMIT 20 OFFSET 0
   ├─ Mapea resultados a DTOs
   └─ Retorna lista

3. Respuesta: 200 OK + List[AppointmentResponse]
```

---

## Autenticación y Autorización

### JWT (JSON Web Token)

**¿Qué es?**
Token firmado que contiene información del usuario. El servidor firma con su secret key.

**Estructura:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJ1c2VyLTEyMyIsInJvbGUiOiJQQVRJRU5UIiwiZXhwIjoxNzEyNDU2MDAwfQ.
xK4Fz9X2jK_L8m3N4o5P6q7r8s9t0u1v2w3x4y5z
```

**Partes:**
1. **Header:** `{ alg: "HS256", typ: "JWT" }`
2. **Payload:** `{ sub: user_id, role: "PATIENT", exp: timestamp }`
3. **Signature:** HMAC(header.payload, secret_key)

**Flujo:**
```
1. Login exitoso
   ├─ Generar payload: { sub, role, exp }
   ├─ Firmar con secret_key
   └─ Retornar token

2. Cada request a endpoint protegido
   ├─ Cliente envía: Authorization: Bearer {token}
   ├─ Servidor verifica signature
   ├─ Si inválido → 401 Unauthorized
   ├─ Si expirado → 401 Unauthorized
   └─ Si válido → Extrae user_id y role

3. Autorización basada en role
   ├─ GET /appointments (requiere admin o doctor)
   ├─ Si role = patient → 403 Forbidden
   └─ Si role = admin → 200 OK
```

### Roles y Permisos

```
┌─────────────────────────────────────────────────┐
│ ENDPOINT                      │ ADMIN │ DOCTOR │ PATIENT │
├─────────────────────────────────────────────────┤
│ POST /doctors                 │  ✓   │   ✗   │   ✗    │
│ GET /doctors                  │  ✓   │   ✓   │   ✓    │
│ POST /patients                │  ✓   │   ✗   │   ✗    │
│ GET /patients                 │  ✓   │   ✗   │   ✗    │
│ POST /appointments            │  ✓   │   ✗   │   ✓    │
│ GET /appointments             │  ✓   │   ✓   │   ✗    │
│ PATCH /appointments/{}/confirm│  ✓   │   ✓   │   ✗    │
│ PATCH /appointments/{}/cancel │  ✓   │   ✓   │   ✓    │
└─────────────────────────────────────────────────┘
```

### Implementación en FastAPI

```python
# dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Valida JWT y retorna usuario"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": user_id, "role": role}

async def require_admin(current_user = Depends(get_current_user)):
    """Only admin"""
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### ✅ **1. AUTH Endpoints**

#### Login
```
POST /auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "Password123!"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

### ✅ **2. DOCTORS Endpoints**

#### Create Doctor (Admin)
```
POST /doctors
Authorization: Bearer {admin_token}
Content-Type: application/json

Request:
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

Response 201:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "...",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "specialty": "Cardiología",
  "license_number": "LIC123456",
  "phone": "+34600000001",
  "consultation_duration": 30,
  "availability": [
    {
      "id": "...",
      "day_of_week": 1,  // Monday
      "start_time": "08:00:00",
      "end_time": "17:00:00",
      "is_active": true
    }
  ],
  "created_at": "2026-04-07T10:00:00"
}
```

#### List All Doctors
```
GET /doctors?skip=0&limit=20
Authorization: Bearer {token}

Response 200:
[
  { doctor object },
  { doctor object },
  ...
]
```

#### Get Doctor by ID
```
GET /doctors/{doctor_id}
Authorization: Bearer {token}

Response 200:
{ doctor object }
```

---

### ✅ **3. PATIENTS Endpoints**

#### Register Patient
```
POST /patients
Content-Type: application/json

Request:
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

Response 201:
{
  "id": "...",
  "email": "patient@example.com",
  "first_name": "María",
  "last_name": "García",
  "full_name": "María García",
  "birth_date": "1990-01-15",
  "phone": "+34600000002",
  "document_number": "12345678A",
  "gender": "F",
  "address": "Calle Principal 123",
  "created_at": "2026-04-07T10:00:00"
}
```

#### List All Patients (Admin)
```
GET /patients?skip=0&limit=20
Authorization: Bearer {admin_token}

Response 200:
[ patient list ]
```

#### Get Patient by ID
```
GET /patients/{patient_id}
Authorization: Bearer {token}

Response 200:
{ patient object }
```

---

### ✅ **4. APPOINTMENTS Endpoints**

#### Create Appointment
```
POST /appointments
Authorization: Bearer {patient_token}
Content-Type: application/json

Request:
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "doctor_id": "660f9511-f40c-52e5-b827-557766551111",
  "scheduled_at": "2026-04-15T10:00:00",
  "duration_minutes": 30,
  "notes": "Revisión general"
}

Response 201:
{
  "id": "...",
  "patient_id": "...",
  "doctor_id": "...",
  "scheduled_at": "2026-04-15T10:00:00",
  "duration_minutes": 30,
  "status": "PENDING",
  "notes": "Revisión general",
  "created_at": "2026-04-07T09:00:00"
}

Error 409 (Slot ocupado):
{
  "detail": "Slot no disponible"
}
```

#### List All Appointments (Admin/Doctor)
```
GET /appointments?skip=0&limit=20&status=PENDING
Authorization: Bearer {admin_token}

Response 200:
{
  "items": [ appointments ],
  "total": 5
}
```

#### Get Appointment by ID
```
GET /appointments/{appointment_id}
Authorization: Bearer {token}

Response 200:
{ appointment object }
```

#### Get Appointments by Patient
```
GET /appointments/patient/{patient_id}?skip=0&limit=20
Authorization: Bearer {patient_token}

Response 200:
[ list of appointments ]
```

#### Get Appointments by Doctor
```
GET /appointments/doctor/{doctor_id}?skip=0&limit=20
Authorization: Bearer {doctor_token}

Response 200:
[ list of appointments ]
```

#### Confirm Appointment (Doctor/Admin)
```
PATCH /appointments/{appointment_id}/confirm
Authorization: Bearer {doctor_token}

Response 200:
{
  "id": "...",
  "status": "CONFIRMED",  // Changed from PENDING
  ...
}
```

#### Cancel Appointment
```
PATCH /appointments/{appointment_id}/cancel
Authorization: Bearer {patient_token}

Response 200:
{
  "id": "...",
  "status": "CANCELLED",  // Changed
  ...
}
```

---

## Patrones de Diseño

### 1. Repository Pattern

**¿Por qué?**
Abstraer acceso a datos. Si cambiamos BD, solo cambiamos implementation.

**Implementación:**
```python
# PORT (Interface - Domain)
class IAppointmentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Appointment:
        pass
    
    @abstractmethod
    async def save(self, appointment: Appointment) -> Appointment:
        pass

# ADAPTER (Implementation - Infrastructure)
class AppointmentRepositoryImpl(IAppointmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, id: UUID) -> Appointment:
        # Query BD real
        result = await self.session.query(AppointmentModel).filter(...)
        return self.map_to_entity(result)
    
    async def save(self, appointment: Appointment) -> Appointment:
        model = self.map_to_model(appointment)
        self.session.add(model)
        await self.session.commit()
        return self.map_to_entity(model)
```

### 2. Use Case Pattern

**¿Por qué?**
Encapsular flujos de negocio. Fácil de testear, reutilizar, modificar.

**Implementación:**
```python
class LoginUseCase:
    def __init__(self, user_repo: IUserRepository, 
                 password_hasher: PasswordHasher,
                 jwt_handler: JWTHandler):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.jwt_handler = jwt_handler
    
    async def execute(self, dto: LoginDTO) -> TokenDTO:
        user = await self.user_repo.find_by_email(dto.email)
        if not user:
            raise UserNotFoundError()
        
        if not self.password_hasher.verify(dto.password, user.password_hash):
            raise InvalidCredentialsError()
        
        token = self.jwt_handler.create_token(user.id, user.role)
        return TokenDTO(access_token=token)
```

### 3. Dependency Injection (FastAPI)

**¿Por qué?**
Facilita testing, desacoplamiento.

**Implementación:**
```python
@router.post("/appointments")
async def create_appointment(
    body: CreateAppointmentRequest,
    session: AsyncSession = Depends(get_db_session),  # Inyectado
    current_user = Depends(get_current_user),          # Inyectado
) -> AppointmentResponse:
    use_case = CreateAppointmentUseCase(
        AppointmentRepositoryImpl(session),
        DoctorRepositoryImpl(session),
        PatientRepositoryImpl(session),
    )
    result = await use_case.execute(dto)
    return AppointmentResponse(**result.__dict__)
```

### 4. DTO (Data Transfer Object)

**¿Por qué?**
Serializar/deserializar entre capas sin exponer entidades.

```python
# Request
class CreateAppointmentRequest(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    notes: str | None = None

# Transfer
class CreateAppointmentDTO:
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    notes: str | None = None

# Response
class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    status: str
    notes: str | None
```

### 5. Value Objects

**¿Por qué?**
Encapsular validaciones, dar semántica de negocio.

```python
class Email(ValueObject):
    value: str
    
    def __init__(self, value: str):
        if not self.is_valid(value):
            raise InvalidEmailError()
        self.value = value
    
    @staticmethod
    def is_valid(email: str) -> bool:
        return "@" in email and "." in email

# En dominio
user = User.create(
    email=Email("user@example.com"),  # Validado aquí
    password_hash=...
)
```

---

## Cómo Funciona Cada Componente

### 1. Entrada de Solicitud (FastAPI Router)

**Archivo:** `app/adapters/http/routes/appointments_routes.py`

```python
@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    body: CreateAppointmentRequest,                      # Schema Pydantic
    session: AsyncSession = Depends(get_db_session),     # BD inyectada
    _current_user = Depends(get_current_user),           # Auth inyectada
) -> AppointmentResponse:
    # 1. Convertir request → DTO
    dto = CreateAppointmentDTO(
        patient_id=body.patient_id,
        doctor_id=body.doctor_id,
        scheduled_at=body.scheduled_at,
        duration_minutes=body.duration_minutes,
        notes=body.notes,
    )
    
    # 2. Ejecutar use case
    result = await _create_uc(session).execute(dto)
    
    # 3. Convertir respuesta → Schema
    return AppointmentResponse(**result.__dict__)
```

**Rol:** 
- Validación de formato HTTP (Pydantic)
- Inyección de dependencias
- Conversión de formatos

---

### 2. Lógica de Negocio (Use Case)

**Archivo:** `app/application/use_cases/appointment/create_appointment.py`

```python
class CreateAppointmentUseCase:
    def __init__(self, app_repo, doctor_repo, patient_repo):
        self.appointment_repo = app_repo
        self.doctor_repo = doctor_repo
        self.patient_repo = patient_repo
    
    async def execute(self, dto: CreateAppointmentDTO) -> Appointment:
        # 1. Validar que doctor y paciente existen
        doctor = await self.doctor_repo.find_by_id(dto.doctor_id)
        if not doctor:
            raise DoctorNotFound()
        
        patient = await self.patient_repo.find_by_id(dto.patient_id)
        if not patient:
            raise PatientNotFound()
        
        # 2. Crear entidad de dominio (con validaciones)
        appointment = Appointment.create(
            patient_id=dto.patient_id,
            doctor_id=dto.doctor_id,
            scheduled_at=dto.scheduled_at,
            duration_minutes=dto.duration_minutes,
            notes=dto.notes,
        )
        
        # 3. Persistir
        return await self.appointment_repo.save(appointment)
```

**Rol:**
- Orquestar flujo de negocio
- Coordinar repositorios
- Ejecutar validades de aplicación

---

### 3. Reglas de Negocio (Domain Entity)

**Archivo:** `app/domain/entities/appointment.py`

```python
class Appointment:
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    status: AppointmentStatus
    notes: str
    
    @staticmethod
    def create(patient_id: UUID, doctor_id: UUID, 
               scheduled_at: datetime, duration_minutes: int,
               notes: str = None) -> "Appointment":
        
        # Validación 1: No pasado
        if scheduled_at <= datetime.now():
            raise FutureScheduledAtRequired()
        
        # Validación 2: Horario laboral (08:00-17:00)
        hour = scheduled_at.hour
        end_hour = (scheduled_at + timedelta(minutes=duration_minutes)).hour
        
        if hour < 8 or end_hour > 17:
            raise OutsideBusinessHoursError()
        
        # Validación 3: No fin de semana
        if scheduled_at.weekday() > 4:  # 5=Viernes, 6=Sábado
            raise WeekendNotAllowedError()
        
        # Si todo OK, crear
        return Appointment(
            id=uuid4(),
            patient_id=patient_id,
            doctor_id=doctor_id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            status=AppointmentStatus.PENDING,
            notes=notes,
        )
```

**Rol:**
- Aplicar reglas de negocio
- Validaciones complejas
- Invariantes

---

### 4. Persistencia (Repository)

**Archivo:** `app/infrastructure/persistence/repositories/appointment_repository_impl.py`

```python
class AppointmentRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, appointment: Appointment) -> Appointment:
        # 1. Convertir entidad domain → modelo SQLAlchemy
        model = AppointmentModel(
            id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            scheduled_at=appointment.scheduled_at,
            duration_minutes=appointment.duration_minutes,
            status=appointment.status.value,  # Enum → string
            notes=appointment.notes,
        )
        
        # 2. Agregar a sesión
        self.session.add(model)
        
        # 3. Ejecutar transacción
        await self.session.commit()
        
        # 4. Actualizar BD refrescar modelo
        await self.session.refresh(model)
        
        # 5. Convertir de vuelta a domain
        return self._map_to_domain(model)
    
    async def find_by_id(self, appointment_id: UUID) -> Appointment:
        result = await self.session.execute(
            select(AppointmentModel).where(AppointmentModel.id == appointment_id)
        )
        model = result.scalars().first()
        if not model:
            return None
        return self._map_to_domain(model)
    
    async def find_overlapping_appointments(
        self, doctor_id: UUID, scheduled_at: datetime, duration: int
    ) -> List[Appointment]:
        """Buscar citas que chocan en horario"""
        end_time = scheduled_at + timedelta(minutes=duration)
        
        result = await self.session.execute(
            select(AppointmentModel).where(
                (AppointmentModel.doctor_id == doctor_id) &
                (AppointmentModel.scheduled_at < end_time) &
                ((AppointmentModel.scheduled_at + 
                  timedelta(minutes=AppointmentModel.duration_minutes)) > scheduled_at) &
                (AppointmentModel.status != "CANCELLED")
            )
        )
        
        models = result.scalars().all()
        return [self._map_to_domain(m) for m in models]
    
    def _map_to_domain(self, model: AppointmentModel) -> Appointment:
        return Appointment(
            id=model.id,
            patient_id=model.patient_id,
            doctor_id=model.doctor_id,
            scheduled_at=model.scheduled_at,
            duration_minutes=model.duration_minutes,
            status=AppointmentStatus(model.status),
            notes=model.notes,
        )
```

**Rol:**
- Query a BD
- Transacciones
- Mapeo domain ↔ BD

---

### 5. Autenticación (JWT & PasswordHasher)

**Archivo:** `app/infrastructure/security/jwt_handler.py`

```python
class JWTHandler:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm
    
    def create_token(self, user_id: UUID, role: UserRole, 
                     expires_minutes: int = 60) -> str:
        # 1. Crear payload
        now = datetime.utcnow()
        expire = now + timedelta(minutes=expires_minutes)
        
        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "role": role.value,
            "exp": expire,        # Expiration
            "iat": now,           # Issued at
        }
        
        # 2. Generar firma
        encoded_jwt = jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
```

**Archivo:** `app/infrastructure/security/password_hasher.py`

```python
class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        # bcrypt hash con salt
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
    
    @staticmethod
    def verify(password: str, hash: str) -> bool:
        # Verificar sin timing attacks
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hash.encode('utf-8')
        )
```

---

### 6. Manejo de Excepciones (Exception Handlers)

**Archivo:** `app/adapters/http/exception_handlers.py`

```python
def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Usuario no encontrado"}
        )
    
    @app.exception_handler(AppointmentSlotUnavailableError)
    async def handle_slot_unavailable(request, exc):
        return JSONResponse(
            status_code=409,
            content={"detail": "Slot no disponible"}
        )
    
    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "Credenciales inválidas"}
        )
```

**Rol:**
- Convertir excepciones domain → HTTP responses
- Consistencia en formato de errores

---

## Resumen Visual

```
REQUEST FLOW
============

1. HTTP Request
   ↓
2. FastAPI Route Handler
   ├─ Pydantic validate schema
   ├─ Inject dependencies (session, auth)
   └─ Convert → DTO
   ↓
3. Use Case Layer
   ├─ Execute business logic
   └─ Repository coordination
   ↓
4. Domain Layer
   ├─ Entity.create() with validations
   └─ Domain exceptions if invalid
   ↓
5. Infrastructure Layer
   ├─ Map entity → Model
   ├─ SQL Query/Insert/Update
   └─ Commit transaction
   ↓
6. Repository
   ├─ Map Model → Entity
   └─ Return to Use Case
   ↓
7. Use Case
   └─ Return result
   ↓
8. Route Handler
   ├─ Map Entity → Response Schema
   ├─ Status Code 201/200
   └─ Serialize → JSON
   ↓
9. HTTP Response

ERROR FLOW
==========

If any step fails:
  ├─ Raise exception
  ├─ Exception Handler catches
  ├─ Converts to HTTP status
  └─ Returns error JSON (400/401/403/404/409/500)
```

---

## Configuración y Secretos

**Archivo:** `.env`

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/saludya

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# App
APP_NAME=Saludya Health Appointments API
APP_VERSION=0.1.0
DEBUG=True
```

**Archivo:** `app/infrastructure/config/settings.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    app_name: str = "Saludya"
    app_version: str = "0.1.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
```

---

## Testing

Aunque no explorado en detalle, la arquitectura permite testing fácil:

```python
# Test sin BD real
@pytest.mark.asyncio
async def test_create_appointment():
    # Mock repositories
    mock_appointment_repo = MagicMock()
    mock_doctor_repo = MagicMock()
    mock_patient_repo = MagicMock()
    
    # Setup mocks
    mock_doctor_repo.find_by_id.return_value = doctor_factory()
    mock_patient_repo.find_by_id.return_value = patient_factory()
    
    # Execute use case
    use_case = CreateAppointmentUseCase(
        mock_appointment_repo,
        mock_doctor_repo,
        mock_patient_repo,
    )
    
    result = await use_case.execute(dto)
    
    # Assert
    assert result.status == AppointmentStatus.PENDING
    assert mock_appointment_repo.save.called
```

---

## Notas de Seguridad

1. **Passwords:** Nunca en log, siempre hasheados con bcrypt
2. **JWT:** Cambiar SECRET_KEY en producción
3. **CORS:** Configurar origen específico en prod
4. **SQL Injection:** SQLAlchemy parametrizado, ya está protegido
5. **HTTPS:** Obligatorio en producción
6. **Rate Limiting:** NO implementado, agregar en producción
7. **Audit Logs:** NO implementado, importante para clínicas

---

## Próximas Mejoras

1. ✅ GET /doctors → YA EXISTE
2. 📧 Notificaciones por email
3. 💬 Sistema de comentarios en citas
4. 📊 Reportes y análisis
5. 🔔 Recordatorios automáticos
6. ⏰ Managing de timeSlots
7. 🏥 Múltiples clínicas
8. 📱 App móvil
9. 🧑‍⚕️ Telemedicina (video calls)

---

**Documento generado:** 2026-04-07
**Versión API:** 0.1.0
**Última actualización:** Incluye análisis completo de arquitectura, flujos y componentes
