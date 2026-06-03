# Guia de Despliegue

## Requisitos

- Python 3.11 o compatible.
- PostgreSQL accesible localmente o en nube.
- Git.
- Variables de entorno configuradas.
- Puerto disponible para la API, por defecto `8000`.

## Instalacion

1. Clonar el repositorio:

```bash
git clone [URL_DEL_REPOSITORIO]
cd saludya-api
```

2. Crear entorno virtual:

```bash
python -m venv venv
```

3. Activar entorno virtual en Windows:

```bash
venv\Scripts\activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Variables de entorno

Crear archivo `.env` en la raiz:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@host:5432/base
DB_ECHO=False
JWT_SECRET_KEY=clave-secreta-segura
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
APP_NAME=Saludya API
APP_VERSION=0.1.0
DEBUG=True
```

## Base de datos

El proyecto usa SQLAlchemy async y requiere que las tablas existan en PostgreSQL.

Entidades requeridas:

- `users`
- `patients`
- `doctors`
- `doctor_availability`
- `appointments`
- Tipo enum `appointment_status` si se usa PostgreSQL enum nativo.

Observacion: no se encontraron migraciones Alembic dentro del repositorio. Para despliegue formal se recomienda crear migraciones o script SQL versionado.

## Ejecucion local

Ejecutar:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Validar:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Ejecucion en produccion

Configurar `.env` o variables del proveedor:

```env
DEBUG=False
DATABASE_URL=postgresql+asyncpg://usuario:password@host-produccion:5432/base
JWT_SECRET_KEY=clave-larga-y-segura
```

Ejecutar con Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Para produccion real se recomienda:

- Usar HTTPS mediante proxy inverso o plataforma cloud.
- No imprimir `DATABASE_URL` en logs.
- Gestionar secretos fuera del repositorio.
- Restringir CORS al dominio real del frontend.
- Agregar migraciones de base de datos.
- Completar Dockerfile o usar servicio PaaS con build Python.

## Docker

El repositorio contiene un archivo `Dockerfile`, pero se encuentra vacio. Por tanto, no hay despliegue Docker funcional derivable del codigo actual.

Plantilla sugerida para completar posteriormente:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Verificacion post-despliegue

| Verificacion | Comando o accion | Esperado |
| --- | --- | --- |
| API levantada | `GET /health` | 200 `status=ok` |
| Docs disponibles | Abrir `/docs` | Swagger UI carga |
| Conexion BD | Ejecutar endpoint que consulte datos | Sin error de conexion |
| Login | `POST /api/v1/auth/login` | Token JWT |
| Seguridad | Endpoint protegido sin token | Rechazo 401/403 |

