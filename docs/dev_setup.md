# Development Setup

## Backend (FastAPI)
1. Create a virtual environment and install deps:
   ```bash
   make install-backend
   ```
2. Run the API:
   ```bash
   make run-backend
   ```
   The server listens on `http://localhost:8000`. Health check at `/health`, dashboard data at `/api/summary`.

## Frontend (React + Vite)
1. Install packages:
   ```bash
   make frontend-install
   ```
2. Start the dev server:
   ```bash
   make frontend-dev
   ```
   Vite proxies `/api` to `http://localhost:8000` by default. Open `http://localhost:5173`.

## Tests
Run Python unit tests:
```bash
make test
```
