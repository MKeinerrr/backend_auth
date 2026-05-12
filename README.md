# backend_auth

Backend REST para autenticación, catálogo de salones y gestión de reservas.

## Stack

- FastAPI
- MySQL (PyMySQL)
- JWT para autenticación
- bcrypt para hash de contraseñas

## Requisitos

- Python 3.10+
- MySQL 8+ (o compatible)
- pip

## Instalación

```bash
cd backend_auth
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

```
## Ejecutar en desarrollo

```bash
cd backend_auth
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Variables de entorno

El proyecto lee un archivo `.env` en esta misma carpeta.

Ejemplo recomendado: (No es el del proyecto)

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=bd_sistema_reserva
DB_PORT=3306

JWT_SECRET=secreto-este-secreto-este-secreto
JWT_EXPIRE_MINUTES=1440

# Origenes permitidos (separados por coma)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
```

Notas:
- `DB_PASSWORD` y `JWT_SECRET` son obligatorios.
- `CORS_ORIGINS` debe contener los dominios que consumen la API.
- Al iniciar, `init_db()` crea base/tablas si no existen.

Documentación automática:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## Endpoints principales

### Auth

- `POST /auth/registro`
	- Body: `{ "nombre": "...", "apellido": "...", "usuario": "...", "correo": "...", "password": "..." }`
	- Registra usuario nuevo.
	- Valida contraseña mínima de 6 y sin espacios.

- `POST /auth/login`
	- Body: `{ "usuario": "...", "password": "..." }`
	- Devuelve token JWT.

- `POST /auth/forgot-password`
	- Paso 1 (solicitar token): `{ "usuario": "..." }`
	- Paso 2 (cambiar clave): `{ "usuario": "...", "new_password": "...", "reset_token": "..." }`
	- Actualiza contraseña con token de verificacion.

### Salones y reservas

- `GET /salones`
	- Lista salones con badges y métricas.

- `POST /reservas`
	- Requiere inicio de sesión. Se debe enviar el token JWT en el header Authorization.
	- Body: `{ "salon_id": 1, "fecha": "2026-05-09", "franja_horaria_id": 2, "asistentes": 50 }`
	- Crea reserva validando disponibilidad, capacidad y franja horaria.

- `GET /reservas/mis`
	- Requiere inicio de sesión. Se debe enviar el token JWT en el header Authorization.
	- Historial de reservas del usuario autenticado.

## Estructura

```text
backend_auth/
	main.py                # App FastAPI y registro de routers
	database.py            # Conexión, bootstrap y migraciones simples
	models.py              # Modelos Pydantic de request/response
	routes/
		auth.py              # Registro, login, cambio de contraseña
		salones.py           # Salones, crear reserva, historial
	utils/
		security.py          # JWT + hash/verify de contraseña
	requirements.txt
```

## Troubleshooting rápido

- Error de conexión a MySQL:
	- Verifica host/puerto/usuario/password en `.env`.
	- Confirma que el servicio MySQL esté activo.

- Error 401 en rutas protegidas:
	- Iniciar sesión otra vez si el token expiró.

- CORS:
	- En desarrollo

## Seguridad

- Contraseñas almacenadas con bcrypt.
- JWT firmado con `JWT_SECRET`.