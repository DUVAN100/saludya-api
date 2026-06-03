# Manual de Usuario

## Alcance del manual

Este manual describe el uso funcional de la API Saludya desde la perspectiva de un usuario final o evaluador usando Swagger UI, ReDoc, Postman o un cliente HTTP equivalente.

No se encontro frontend dentro del repositorio, por lo que las acciones se documentan sobre los endpoints disponibles.

## Como ingresar al sistema

1. Ejecutar el backend.
2. Abrir Swagger UI en:

```text
http://localhost:8000/docs
```

3. Registrar o disponer de un usuario existente.
4. Iniciar sesion en `POST /api/v1/auth/login`.
5. Copiar el valor `access_token`.
6. En Swagger, usar el boton de autorizacion e ingresar:

```text
Bearer TOKEN_OBTENIDO
```

[INSERTAR CAPTURA AQUÍ]

## Funcionalidades disponibles

### Autenticacion

Permite iniciar sesion con email y contrasena.

Ejemplo:

```json
{
  "email": "doctor@clinic.com",
  "password": "secret123"
}
```

Resultado esperado:

```json
{
  "access_token": "jwt_generado",
  "token_type": "bearer"
}
```

[INSERTAR CAPTURA AQUÍ]

### Registro de paciente

Permite crear un paciente nuevo con usuario asociado.

Ejemplo:

```json
{
  "email": "juan@email.com",
  "password": "secret123",
  "first_name": "Juan",
  "last_name": "Garcia",
  "birth_date": "1990-05-15",
  "document_number": "12345678",
  "document_type": "CC",
  "gender": "M"
}
```

[INSERTAR CAPTURA AQUÍ]

### Consulta de pacientes

El administrador puede listar pacientes usando:

```http
GET /api/v1/patients?skip=0&limit=20
```

[INSERTAR CAPTURA AQUÍ]

### Creacion de medico

El administrador puede crear un medico.

Ejemplo:

```json
{
  "email": "dr.carlos@clinic.com",
  "password": "secret123",
  "first_name": "Carlos",
  "last_name": "Perez",
  "specialty": "Cardiologia",
  "license_number": "MED-001",
  "consultation_duration": 30
}
```

El sistema crea disponibilidad por defecto de lunes a viernes, 08:00 a 17:00.

[INSERTAR CAPTURA AQUÍ]

### Consulta de medicos

Usuarios autenticados pueden consultar medicos:

```http
GET /api/v1/doctors
GET /api/v1/doctors/{doctor_id}
```

[INSERTAR CAPTURA AQUÍ]

### Agendamiento de cita

Usuarios autenticados pueden agendar citas.

Ejemplo:

```json
{
  "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "doctor_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "scheduled_at": "2026-06-10T10:00:00-05:00",
  "duration_minutes": 30,
  "notes": "Primera consulta"
}
```

Condiciones importantes:

- La fecha debe incluir zona horaria.
- La cita debe ser futura.
- Solo se permite lunes a viernes.
- El horario valido es 08:00 a 17:00.
- No se permite doble reserva para el mismo medico y hora.

[INSERTAR CAPTURA AQUÍ]

### Confirmar cita

Medicos o administradores pueden confirmar una cita:

```http
PATCH /api/v1/appointments/{appointment_id}/confirm
```

[INSERTAR CAPTURA AQUÍ]

### Cancelar cita

Usuarios autenticados pueden cancelar una cita:

```http
PATCH /api/v1/appointments/{appointment_id}/cancel
```

[INSERTAR CAPTURA AQUÍ]

### Consultar citas

Endpoints disponibles:

```http
GET /api/v1/appointments/{appointment_id}
GET /api/v1/appointments/patient/{patient_id}
GET /api/v1/appointments/doctor/{doctor_id}
GET /api/v1/appointments
```

[INSERTAR CAPTURA AQUÍ]

## Mensajes de error comunes

| Situacion | Codigo esperado | Explicacion |
| --- | --- | --- |
| Token invalido o vencido | 401 | El usuario debe iniciar sesion nuevamente. |
| Rol insuficiente | 403 | El usuario no tiene permisos para ejecutar la accion. |
| Recurso no encontrado | 404 | El ID enviado no existe en base de datos. |
| Email, documento o slot duplicado | 409 | Existe un conflicto de negocio. |
| Datos invalidos | 422 | Validacion de Pydantic o regla de negocio incumplida. |


