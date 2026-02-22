# Gymyo

Aplicación de entrenamiento adaptativo con backend en **FastAPI** y frontend en **React + Vite + TypeScript**.

## Requisitos

- Python 3.10+
- Node.js 18+
- npm 9+
- PostgreSQL (opcional para desarrollo rápido si ya tienes una instancia local)

## Estructura del proyecto

- `app/`: backend FastAPI (lógica fisiológica, motor de decisión, API y persistencia)
- `web/`: frontend React + Vite
- `tests/`: pruebas unitarias del motor
- `docs/USAGE.md`: guía breve de uso de la UI

## Configuración local

### 1) Clonar e ingresar al proyecto

```bash
git clone <tu-repo>
cd gymyo
```

### 2) Backend (Python)

Crear entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

> Si necesitas dependencias de testing:

```bash
pip install -e .[test]
```

Configurar base de datos (por defecto usa):

```text
postgresql+psycopg://postgres:postgres@localhost:5432/gymyo
```

Puedes sobrescribir con variable de entorno:

```bash
export DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/gymyo"
```

### 3) Frontend (React + Vite)

```bash
cd web
npm install
cd ..
```

## Ejecutar en desarrollo

Con un solo comando (backend + Vite):

```bash
make dev
```

Servicios:

- Frontend: `http://localhost:5173`
- API backend: `http://localhost:8000/api`

La configuración de Vite ya incluye proxy `/api -> http://localhost:8000`.

## Ejecutar solo backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Build de frontend para producción

```bash
make web-build
```

Esto genera `web/dist`.

## Ejecutar modo producción local

FastAPI sirve archivos estáticos desde `web/dist`:

```bash
make run
```

Abrir en navegador:

- App: `http://localhost:8000`
- API: `http://localhost:8000/api/...`

## Endpoints principales

- `GET /api/profile`
- `PUT /api/profile`
- `POST /api/log-session`
- `POST /api/update-metrics`
- `GET /api/next-workout`
- `GET /api/analytics`
- `GET /api/dashboard`

## Pruebas

```bash
pytest
```

## Solución de problemas

- Si falla la conexión a PostgreSQL, verifica `DATABASE_URL` y que la base exista.
- Si `npm install` falla por proxy/red, configura npm para tu entorno corporativo.
- Si no se ve la UI en `:8000`, ejecuta primero `make web-build`.
