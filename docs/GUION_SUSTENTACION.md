# Guion de Sustentacion - 15 minutos

## 1. Presentacion del equipo - 1 minuto

Buenos dias/tardes. Somos el equipo encargado del desarrollo de Saludya API, un sistema backend para la gestion de citas medicas. Cada integrante participo en actividades de analisis, desarrollo, pruebas y documentacion.

Integrantes:

- [EDITAR: Nombre 1] - [Rol]
- [EDITAR: Nombre 2] - [Rol]
- [EDITAR: Nombre 3] - [Rol]

## 2. Problema resuelto - 2 minutos

El problema identificado es la gestion manual o desorganizada de citas medicas. Esto puede generar errores como doble reserva, falta de control de disponibilidad, dificultad para consultar agendas y poca trazabilidad.

Saludya API resuelve este problema ofreciendo una API REST que permite registrar pacientes, crear medicos, autenticar usuarios y gestionar citas con reglas de negocio claras.

Puntos clave:

- Centralizacion de informacion.
- Autenticacion con roles.
- Validacion de horario laboral.
- Prevencion de doble reserva.
- Consulta de citas por medico, paciente o listado general.

## 3. Arquitectura - 3 minutos

El proyecto se construyo con FastAPI y una arquitectura por capas:

- `adapters`: expone rutas HTTP, schemas y dependencias.
- `application`: contiene casos de uso y DTOs.
- `domain`: concentra entidades y reglas de negocio.
- `infrastructure`: implementa base de datos, repositorios, seguridad y configuracion.

Flujo resumido:

1. Cliente consume endpoint.
2. FastAPI valida datos con Pydantic.
3. Se valida JWT y rol si aplica.
4. Se ejecuta un caso de uso.
5. El caso de uso aplica reglas de dominio y usa repositorios.
6. SQLAlchemy persiste o consulta en PostgreSQL.
7. La API retorna respuesta JSON.

## 4. Demostracion funcional - 5 minutos

Orden recomendado de demo:

1. Abrir Swagger en `/docs`.
2. Mostrar health check `/health`.
3. Registrar paciente con `POST /api/v1/patients`.
4. Iniciar sesion con `/api/v1/auth/login`.
5. Autorizar Swagger con token Bearer.
6. Crear medico como administrador.
7. Listar medicos.
8. Crear cita con fecha futura, en horario laboral y con zona horaria.
9. Confirmar cita como medico o administrador.
10. Cancelar cita como usuario autenticado.

Mensajes para destacar:

- El sistema rechaza fechas sin zona horaria.
- El sistema rechaza citas en pasado o fuera de horario.
- El sistema protege endpoints con JWT.
- Algunos endpoints requieren rol admin o doctor.

## 5. Pruebas realizadas - 2 minutos

Se definio un plan de pruebas funcionales con 42 casos que cubren:

- Casos exitosos.
- Casos fallidos.
- Validaciones de request.
- Manejo de errores.
- Seguridad basica por token y roles.

Ejemplos:

- Login exitoso e invalido.
- Registro de paciente con datos validos e invalidos.
- Creacion de medico solo por admin.
- Agendamiento de cita valida.
- Rechazo de cita en fin de semana, fuera de horario o con slot ocupado.

## 6. Conclusiones - 2 minutos

Saludya API entrega una base funcional para la gestion de citas medicas. La arquitectura facilita mantenimiento, pruebas y extension futura.

Conclusiones principales:

- El dominio esta separado de FastAPI y SQLAlchemy.
- Las reglas de negocio principales estan centralizadas.
- La autenticacion por JWT permite proteger operaciones.
- El sistema puede integrarse posteriormente con un frontend web.

Trabajo futuro recomendado:

- Agregar frontend.
- Implementar migraciones Alembic.
- Completar Dockerfile.
- Mejorar logging y remover prints de depuracion.
- Automatizar pruebas funcionales e integracion continua.

