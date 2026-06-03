# Casos de Uso

## Actores identificados

| Actor | Descripcion |
| --- | --- |
| Administrador | Usuario con rol `admin`; puede crear medicos y consultar listados administrativos. |
| Medico | Usuario con rol `doctor`; puede consultar agenda y confirmar citas. |
| Paciente | Usuario con rol `patient`; puede registrarse, autenticarse y solicitar citas. |
| Sistema | API que valida reglas, tokens, disponibilidad y persistencia. |

## CU-01 - Iniciar sesion

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario registrado |
| Modulo | Autenticacion |
| Endpoint | `POST /api/v1/auth/login` |
| Flujo principal | 1. El usuario envia email y password. 2. El sistema busca el usuario por email. 3. Valida la contrasena con bcrypt. 4. Verifica que el usuario este activo. 5. Genera JWT. |
| Flujo alternativo | Si el email no existe, la contrasena no coincide o el usuario esta inactivo, retorna error de autenticacion. |
| Resultado esperado | Token Bearer valido con `access_token` y `token_type`. |

## CU-02 - Registrar paciente

| Campo | Detalle |
| --- | --- |
| Actor principal | Paciente |
| Modulo | Pacientes |
| Endpoint | `POST /api/v1/patients` |
| Flujo principal | 1. El paciente envia datos personales, email y password. 2. El sistema valida formato y longitud. 3. Verifica que el email no exista. 4. Verifica documento unico si fue enviado. 5. Crea usuario con rol `patient`. 6. Crea perfil de paciente. |
| Flujo alternativo | Email duplicado o documento duplicado genera conflicto. Datos invalidos generan error de validacion. |
| Resultado esperado | Paciente registrado con ID, user_id, nombre completo y fecha de creacion. |

## CU-03 - Listar pacientes

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Modulo | Pacientes |
| Endpoint | `GET /api/v1/patients` |
| Flujo principal | 1. El administrador envia token Bearer. 2. El sistema valida rol admin. 3. Aplica paginacion `skip` y `limit`. 4. Retorna pacientes. |
| Flujo alternativo | Sin token retorna 401. Rol diferente de admin retorna 403. |
| Resultado esperado | Lista de pacientes. |

## CU-04 - Consultar paciente por ID

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario autenticado |
| Modulo | Pacientes |
| Endpoint | `GET /api/v1/patients/{patient_id}` |
| Flujo principal | 1. El usuario envia token. 2. El sistema valida JWT. 3. Busca el paciente por UUID. |
| Flujo alternativo | Paciente inexistente retorna 404. Token invalido retorna 401. |
| Resultado esperado | Datos del paciente solicitado. |

## CU-05 - Crear medico

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Modulo | Medicos |
| Endpoint | `POST /api/v1/doctors` |
| Flujo principal | 1. Admin envia datos del medico. 2. El sistema valida token y rol. 3. Valida email, password, especialidad, licencia y duracion. 4. Crea usuario con rol `doctor`. 5. Crea perfil medico. 6. Crea disponibilidad por defecto lunes a viernes 08:00-17:00. |
| Flujo alternativo | Email duplicado, licencia duplicada, datos invalidos o rol no autorizado generan error. |
| Resultado esperado | Medico creado con disponibilidad base. |

## CU-06 - Listar medicos

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario autenticado |
| Modulo | Medicos |
| Endpoint | `GET /api/v1/doctors` |
| Flujo principal | 1. Usuario envia token. 2. El sistema valida token. 3. Aplica paginacion. 4. Retorna medicos. |
| Flujo alternativo | Token ausente o invalido retorna 401. |
| Resultado esperado | Lista de medicos disponibles en el sistema. |

## CU-07 - Consultar medico por ID

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario autenticado |
| Modulo | Medicos |
| Endpoint | `GET /api/v1/doctors/{doctor_id}` |
| Flujo principal | 1. Usuario envia token. 2. El sistema valida JWT. 3. Busca medico con disponibilidad. |
| Flujo alternativo | Medico inexistente retorna 404. Token invalido retorna 401. |
| Resultado esperado | Datos del medico y disponibilidad. |

## CU-08 - Agendar cita

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario autenticado |
| Modulo | Citas |
| Endpoint | `POST /api/v1/appointments` |
| Flujo principal | 1. Usuario envia token. 2. Envia patient_id, doctor_id, scheduled_at con zona horaria, duracion y notas. 3. El sistema valida existencia de paciente y medico. 4. Valida disponibilidad del medico. 5. Valida que el slot no este ocupado. 6. Valida fecha futura y horario lunes a viernes 08:00-17:00. 7. Crea cita en estado `pending`. |
| Flujo alternativo | Paciente o medico inexistente retorna 404. Medico no disponible, cita en pasado u horario invalido retorna 422. Slot ocupado retorna 409. |
| Resultado esperado | Cita creada. |

## CU-09 - Confirmar cita

| Campo | Detalle |
| --- | --- |
| Actor principal | Medico o Administrador |
| Modulo | Citas |
| Endpoint | `PATCH /api/v1/appointments/{appointment_id}/confirm` |
| Flujo principal | 1. Actor envia token. 2. El sistema valida rol admin o doctor. 3. Busca la cita. 4. Cambia estado de `pending` a `confirmed`. |
| Flujo alternativo | Cita inexistente retorna 404. Transicion invalida retorna 422. Rol no autorizado retorna 403. |
| Resultado esperado | Cita confirmada. |

## CU-10 - Cancelar cita

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario autenticado |
| Modulo | Citas |
| Endpoint | `PATCH /api/v1/appointments/{appointment_id}/cancel` |
| Flujo principal | 1. Usuario envia token. 2. El sistema busca la cita. 3. Cambia estado permitido a `cancelled`. |
| Flujo alternativo | Cita inexistente retorna 404. Transicion invalida retorna 422. Token invalido retorna 401. |
| Resultado esperado | Cita cancelada. |

## CU-11 - Consultar citas

| Campo | Detalle |
| --- | --- |
| Actor principal | Usuario autenticado, Medico o Administrador segun endpoint |
| Modulo | Citas |
| Endpoints | `GET /api/v1/appointments/{id}`, `GET /api/v1/appointments/patient/{patient_id}`, `GET /api/v1/appointments/doctor/{doctor_id}`, `GET /api/v1/appointments` |
| Flujo principal | 1. Actor envia token. 2. El sistema valida permisos. 3. Consulta por ID, paciente, medico o listado general. |
| Flujo alternativo | Token invalido retorna 401. Rol insuficiente retorna 403. Cita inexistente retorna 404. |
| Resultado esperado | Datos de cita o listas paginadas. |

## CU-12 - Consultar salud de la API

| Campo | Detalle |
| --- | --- |
| Actor principal | Equipo tecnico |
| Modulo | Salud |
| Endpoint | `GET /health` |
| Flujo principal | 1. Se invoca el endpoint. 2. La API retorna estado y version. |
| Flujo alternativo | Si la aplicacion no esta levantada, no hay respuesta HTTP. |
| Resultado esperado | `{ "status": "ok", "version": "..." }`. |

