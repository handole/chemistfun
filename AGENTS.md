# AGENTS.md

KimiFun: Chemistry learning platform, virtual lab, and assessment system for Indonesian high schools (SMA X/XI/XII).

## Architecture

- **Backend**: Python 3.10+, FastAPI (`backend/app/main.py`), SQLAlchemy 2.0 (AsyncPG), PostgreSQL 16
  - Auto-migration: startup runs `Base.metadata.create_all` via `lifespan` in `app/main.py`. No Alembic.
  - Table definitions must be imported in `app/modules/__init__.py` to register with `Base.metadata`.
  - Auth: PBKDF2-HMAC-SHA256 (`app/core/security.py`) + JWT. Teacher registration requires `TEACHER_INVITE_CODE`.
  - Rate limiting in `app/core/rate_limiter.py` affects `/auth/login` and `/auth/register`.
- **Frontend**: Vue 3 (Composition API), Vite, Tailwind CSS, Lucide icons (`frontend/src/`)
  - SPA without Vue Router: views switch via `currentTab` in `frontend/src/App.vue`.
  - API client in `frontend/src/api/client.js` proxies `/api` via Vite dev server or Docker network.
  - Stores auth token in `localStorage.getItem('KimiFun_token')`.
- **Mobile**: Flutter app (`mobile/`) targeting Android/iOS, communicates with FastAPI backend.
- **Docker**: Root `docker-compose.yml` orchestrates PostgreSQL, backend (port 8000), frontend (port 5173).

## Setup & Run Commands

### Docker (Recommended)
```bash
cp .env.example .env
cp backend/.env.example backend/.env
docker compose up -d --build
```

### Local Dev (No Docker)
- **PostgreSQL**: Must run on `localhost:5432` with credentials matching `.env`.
- **Backend**:
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- **Mobile**:
  ```bash
  cd mobile
  flutter pub get
  flutter run
  ```

## Testing & Verification

### Frontend Unit Tests (Vitest)
```bash
cd frontend
npm test               # Run all Vitest suites
npx vitest run tests/unit/app-smoke.test.mts  # Single test file
```
Note: Vitest uses `happy-dom`. API network calls during component mount will fail harmlessly with `ECONNREFUSED` if backend is not running.

### Backend Contract Tests (Pytest)
```bash
# Prerequisites: server running at http://127.0.0.1:8000 + pip dependencies installed
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
pytest tests/test_api.py -k test_health_endpoint  # Single test
```
- Tests hit live HTTP endpoints via `fastapi.testclient.TestClient`.
- Certain tests return 404 or fail unless database has seeded data (see `README_TESTS.md`).

### Stress Testing
```bash
cd backend
python3 stress_test.py  # Tests concurrent requests & latency against live backend
```

### Lint & Typecheck (CI Standard)
CI runs these steps (`.github/workflows/ci.yml`):
```bash
# Backend
cd backend
ruff check .
mypy .
bandit -r .

# Frontend
cd frontend
npm run test
npm run build
```

## Important Quirks & Conventions

- **API Routing**: All application endpoints mounted under `/api` (`/api/auth`, `/api/classes`, `/api/content`, `/api/assessment`, `/api/journals`). Health check is dual-mounted at `/health` and `/api/health`.
- **CORS Config**: Supports Tailscale Funnel (`*.ts.net`) and Tailscale IP (`100.x.y.z`) via regex in `app/core/config.py`.
- **Teacher Registration**: Requires setting `TEACHER_INVITE_CODE` in `.env` matching input code. Student registration does not require invite code.
- **Chemistry Math Rendering**: Frontend uses KaTeX (`frontend/src/utils/mathjax.js` & `formula.js`) for rendering formulas and TeX expressions.
- **AI Services**: Switchable via `AI_PROVIDER` (`9router` or `gemini`). 9router uses OpenAI-compatible format with endpoint configured in `.env`.
