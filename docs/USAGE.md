# Usage

## Web UI

### Prerequisites
- Python environment with backend dependencies installed.
- Node.js 18+ and npm.

### Development mode (FastAPI + Vite)
```bash
make dev
```
- Backend API: `http://localhost:8000/api`
- Web UI: `http://localhost:5173`

### Build web bundle
```bash
make web-build
```

### Run production-style server (serves `/web/dist` from FastAPI)
```bash
make run
```
Then open `http://localhost:8000`.
