# Plan de Pruebas Funcionales

## Objetivo

Validar que los modulos funcionales del backend Saludya API cumplen los flujos principales, validaciones, seguridad basica y manejo de errores observados en el codigo fuente.

## Alcance

Incluye pruebas funcionales sobre:

- Autenticacion.
- Pacientes.
- Medicos.
- Citas.
- Seguridad por JWT y roles.
- Health check.

No incluye pruebas de interfaz grafica porque el repositorio no contiene frontend.

## Datos requeridos

| Dato | Descripcion |
| --- | --- |
| Usuario admin | Usuario con rol `admin` creado previamente en base de datos. |
| Usuario doctor | Usuario con rol `doctor` creado al crear medico. |
| Usuario paciente | Usuario con rol `patient` creado al registrar paciente. |
| Base PostgreSQL | Base configurada en `DATABASE_URL`. |
| Token JWT | Token obtenido con `/api/v1/auth/login`. |

## Casos de prueba

| ID | Modulo | Caso de prueba | Precondicion | Pasos | Resultado esperado |
| -- | ------ | -------------- | ------------ | ----- | ------------------ |
| PF-001 | Salud | Consultar estado de API | API ejecutandose | 1. Enviar `GET /health`. | Retorna 200 con `status=ok` y `version`. |
| PF-002 | Autenticacion | Login exitoso | Usuario activo existente | 1. Enviar email y password correctos a `/api/v1/auth/login`. | Retorna 200 con `access_token` y `token_type=bearer`. |
| PF-003 | Autenticacion | Login con password incorrecto | Usuario existente | 1. Enviar email valido y password incorrecto. | Retorna 401 por credenciales invalidas. |
| PF-004 | Autenticacion | Login con email inexistente | Ninguna | 1. Enviar email que no existe. | Retorna 401 por credenciales invalidas. |
| PF-005 | Seguridad | Acceder sin token a endpoint protegido | API ejecutandose | 1. Enviar `GET /api/v1/doctors` sin header Authorization. | Retorna 401/403 segun HTTPBearer. |
| PF-006 | Seguridad | Acceder con token invalido | Token alterado | 1. Enviar token invalido a endpoint protegido. | Retorna 401 con detalle de token invalido o expirado. |
| PF-007 | Seguridad | Acceder a recurso admin con rol no admin | Token doctor o patient | 1. Enviar `GET /api/v1/patients`. | Retorna 403 por rol insuficiente. |
| PF-008 | Pacientes | Registrar paciente exitosamente | Email y documento no usados | 1. Enviar `POST /api/v1/patients` con datos validos. | Retorna 201 con datos del paciente. |
| PF-009 | Pacientes | Registrar paciente con email invalido | Ninguna | 1. Enviar email sin formato valido. | Retorna 422 por validacion. |
| PF-010 | Pacientes | Registrar paciente con password corta | Ninguna | 1. Enviar password menor a 8 caracteres. | Retorna 422 por validacion. |
| PF-011 | Pacientes | Registrar paciente con documento duplicado | Paciente ya registrado con documento | 1. Enviar nuevo registro con mismo `document_number`. | Retorna 409 por paciente existente. |
| PF-012 | Pacientes | Registrar paciente con tipo de documento invalido | Ninguna | 1. Enviar `document_type` fuera de `CC`, `CE`, `TI`, `PP`. | Retorna 422. |
| PF-013 | Pacientes | Listar pacientes como admin | Token admin valido | 1. Enviar `GET /api/v1/patients?skip=0&limit=20`. | Retorna 200 con lista. |
| PF-014 | Pacientes | Consultar paciente por ID existente | Token valido y paciente existente | 1. Enviar `GET /api/v1/patients/{id}`. | Retorna 200 con paciente. |
| PF-015 | Pacientes | Consultar paciente inexistente | Token valido | 1. Enviar UUID valido inexistente. | Retorna 404. |
| PF-016 | Medicos | Crear medico como admin | Token admin, email y licencia libres | 1. Enviar `POST /api/v1/doctors` con datos validos. | Retorna 201 con medico y disponibilidad. |
| PF-017 | Medicos | Crear medico sin permisos | Token patient | 1. Enviar `POST /api/v1/doctors`. | Retorna 403. |
| PF-018 | Medicos | Crear medico con email duplicado | Email existente | 1. Enviar email ya registrado. | Retorna 409 o error de dominio por usuario existente. |
| PF-019 | Medicos | Crear medico con licencia duplicada | Licencia existente | 1. Enviar `license_number` ya registrado. | Retorna error por licencia duplicada. |
| PF-020 | Medicos | Crear medico con duracion invalida | Token admin | 1. Enviar `consultation_duration` menor a 10 o mayor a 120. | Retorna 422. |
| PF-021 | Medicos | Listar medicos | Token valido | 1. Enviar `GET /api/v1/doctors`. | Retorna 200 con lista. |
| PF-022 | Medicos | Consultar medico por ID | Token valido y medico existente | 1. Enviar `GET /api/v1/doctors/{id}`. | Retorna 200 con medico. |
| PF-023 | Medicos | Consultar medico inexistente | Token valido | 1. Enviar UUID inexistente. | Retorna 404. |
| PF-024 | Citas | Crear cita exitosa | Token valido, paciente y medico existentes, disponibilidad activa | 1. Enviar fecha futura lunes-viernes 08:00-17:00 con zona horaria. | Retorna 201 con cita en estado `pending`. |
| PF-025 | Citas | Crear cita sin zona horaria | Token valido | 1. Enviar `scheduled_at` sin offset. | Retorna 422. |
| PF-026 | Citas | Crear cita en el pasado | Token valido | 1. Enviar fecha anterior a la actual. | Retorna 422. |
| PF-027 | Citas | Crear cita fuera de horario | Token valido | 1. Enviar hora menor a 08:00 o igual/mayor a 17:00. | Retorna 422. |
| PF-028 | Citas | Crear cita en fin de semana | Token valido | 1. Enviar sabado o domingo. | Retorna 422. |
| PF-029 | Citas | Crear cita con medico inexistente | Token valido y patient existente | 1. Enviar `doctor_id` inexistente. | Retorna 404. |
| PF-030 | Citas | Crear cita con paciente inexistente | Token valido y doctor existente | 1. Enviar `patient_id` inexistente. | Retorna 404. |
| PF-031 | Citas | Crear cita en slot ocupado | Cita activa existente mismo medico/hora | 1. Enviar nueva cita con mismo `doctor_id` y `scheduled_at`. | Retorna 409. |
| PF-032 | Citas | Confirmar cita pendiente | Token admin o doctor, cita pending | 1. Enviar `PATCH /api/v1/appointments/{id}/confirm`. | Retorna 200 con estado `confirmed`. |
| PF-033 | Citas | Confirmar cita con rol paciente | Token patient | 1. Enviar confirmacion. | Retorna 403. |
| PF-034 | Citas | Confirmar cita inexistente | Token admin o doctor | 1. Enviar UUID inexistente. | Retorna 404. |
| PF-035 | Citas | Cancelar cita pendiente o confirmada | Token valido, cita activa | 1. Enviar `PATCH /api/v1/appointments/{id}/cancel`. | Retorna 200 con estado `cancelled`. |
| PF-036 | Citas | Cancelar cita ya cancelada | Token valido, cita cancelada | 1. Enviar cancelacion nuevamente. | Retorna 422 por transicion invalida. |
| PF-037 | Citas | Consultar cita por ID | Token valido, cita existente | 1. Enviar `GET /api/v1/appointments/{id}`. | Retorna 200 con cita. |
| PF-038 | Citas | Listar citas por paciente | Token valido | 1. Enviar `GET /api/v1/appointments/patient/{patient_id}`. | Retorna 200 con lista. |
| PF-039 | Citas | Listar citas por medico | Token admin o doctor | 1. Enviar `GET /api/v1/appointments/doctor/{doctor_id}`. | Retorna 200 con lista. |
| PF-040 | Citas | Listar todas las citas con filtro | Token admin o doctor | 1. Enviar `GET /api/v1/appointments?status=pending`. | Retorna 200 con `items` y `total`. |
| PF-041 | Citas | Listar todas las citas con rol paciente | Token patient | 1. Enviar `GET /api/v1/appointments`. | Retorna 403. |
| PF-042 | Validacion | Paginacion invalida | Token valido | 1. Enviar `limit=0` o `limit=101`. | Retorna 422. |

## Criterios de aceptacion

- Todos los flujos exitosos deben retornar codigos 200 o 201 segun endpoint.
- Todas las validaciones deben retornar 422 cuando el error proviene del request o regla de negocio procesable.
- Los conflictos de unicidad o slot ocupado deben retornar 409 cuando existe handler asociado.
- Los accesos no autenticados o con token invalido deben rechazarse.
- Los accesos con rol insuficiente deben retornar 403.

