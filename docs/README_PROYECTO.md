# Saludya API - Documentacion de Proyecto

## Descripcion general

Saludya API es un backend REST para la gestion de citas medicas. El sistema permite registrar pacientes, crear medicos, autenticar usuarios mediante JWT y administrar citas medicas con validaciones de disponibilidad, horario laboral y estado de la cita.

El repositorio analizado corresponde al backend de la solucion. No se encontraron componentes React ni una aplicacion frontend dentro del codigo fuente disponible.

## Objetivo del sistema

Centralizar el proceso de agendamiento de citas medicas mediante una API que permita:

- Registrar pacientes con informacion personal y documento.
- Crear medicos con especialidad, licencia profesional y disponibilidad base.
- Autenticar usuarios con correo y contrasena.
- Crear, consultar, confirmar y cancelar citas.
- Controlar reglas basicas de negocio como horarios permitidos, citas futuras y prevencion de doble reserva.

## Tecnologias utilizadas

| Categoria | Tecnologia |
| --- | --- |
| Lenguaje | Python 3.11 |
| Framework API | FastAPI |
| Servidor ASGI | Uvicorn |
| ORM | SQLAlchemy async |
| Base de datos | PostgreSQL compatible con asyncpg |
| Validacion | Pydantic v2 |
| Configuracion | pydantic-settings, python-dotenv |
| Seguridad | JWT con python-jose, bcrypt/passlib |
| Pruebas | Pytest declarado como herramienta recomendada en documentacion y requirements actuales |

## Integrantes

| Nombre | Rol | Observaciones |
| --- | --- | --- |
| [EDITAR] | [EDITAR] | [EDITAR] |
| [EDITAR] | [EDITAR] | [EDITAR] |
| [EDITAR] | [EDITAR] | [EDITAR] |

## Alcance

### Incluido en el repositorio

- API REST con FastAPI.
- Arquitectura por capas: adapters, application, domain e infrastructure.
- Modelos de dominio para usuario, paciente, medico, disponibilidad y cita.
- Casos de uso para login, registro/listado de pacientes, creacion/listado de medicos y gestion de citas.
- Modelos SQLAlchemy para persistencia.
- Autenticacion por token Bearer JWT.
- Manejo centralizado de excepciones de dominio.

### No incluido en el repositorio

- Frontend React o pantallas de usuario.
- Migraciones de base de datos con Alembic.
- Archivo `docker-compose.yml`.
- Dockerfile funcional; el archivo existe, pero se encuentra vacio.
- Coleccion Postman dentro del arbol actual de archivos.

## Modulos funcionales identificados

| Modulo | Descripcion |
| --- | --- |
| Autenticacion | Login de usuarios y generacion de token JWT. |
| Pacientes | Registro, listado administrativo y consulta por ID. |
| Medicos | Creacion administrativa, listado y consulta por ID. |
| Citas | Creacion, consulta, confirmacion, cancelacion y listados filtrados. |
| Seguridad | Validacion de token, roles admin/doctor/patient y proteccion de endpoints. |
| Salud del sistema | Endpoint `/health` para verificar estado basico de la API. |

