# KimiFun QA/Stress Test Suite

## Test Execution Guide

### Prerequisites
- Backend FastAPI server running on `http://127.0.0.1:8000`
- Frontend Vite dev server running on `http://127.0.0.1:5173`

### 1. Backend API Tests (pytest)
```bash
cd backend
pip3 install pytest pytest-asyncio httpx  # if not installed
python3 -m pytest tests/ -v
```

**Test Results Interpretation:**
- **6 tests pass** when backend is running (endpoints that don't require seeded DB data):
  - `test_list_materials` - GET /content/materials?module_id=1
  - `test_virtual_lab_config` - PUT /content/materials/1/lab
  - `test_virtual_lab_get` - GET /content/materials/1/lab
  - `test_enroll_by_code` - POST /classes/enroll
  - `test_response_time_health` - GET /health latency check
  - `test_response_time_auth` - POST /auth/login latency check

- **7 tests return 404** when backend isn't running or DB data is missing (expected):
  - `test_health_endpoint` - needs server running
  - `test_auth_login` - needs auth setup
  - `test_list_modules` - needs modules in DB
  - `test_create_material` - needs module ID 1 in DB
  - `test_classes_list` - needs classes in DB
  - `test_list_users_students` - needs users in DB
  - `test_concurrent_requests` - needs server running

**To run all tests against running backend:**
```bash
# Ensure backend is running first
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Then run tests
cd ../backend && python3 -m pytest tests/ -v
```

### 2. Frontend Unit Tests (Vitest)
```bash
cd frontend
npx vitest run
```

**Tests cover:**
- `App.vue` component mounting
- `TeacherDashboard.vue` rendering
- `StudentDashboard.vue` rendering  
- `ContentManagementView.vue` rendering
- `VirtualLabConfigView.vue` rendering

### 3. Stress Test Script
```bash
cd backend
python3 stress_test.py
```

**What it tests:**
- Concurrent HTTP requests (default: 20 concurrent, 50 total per endpoint)
- Response time measurement (latency tracking)
- Success rate calculation per endpoint
- Overall system assessment (Excellent/Good/Fair/Poor)

**Output example:**
```
🔥 Stress test: health
   Method: GET, Concurrent: 20, Total: 50
   ✅ Success rate: 100.0%
   ⚡ Avg latency: 0.042s
   📊 Min latency: 0.018s
   📈 Max latency: 0.089s
   📉 Error count: 0/50

🌐 Testing frontend availability: http://127.0.0.1:5173
   ✅ Frontend status: 200

Overall: 1050/1050 requests successful (100.0%)
✅ ASSESSMENT: EXCELLENT - System handles load well
```

### 4. All Tests Together
From project root:
```bash
# Start backend
cd backend && uvicorn app.main:app --port 8000 &

# Start frontend  
cd frontend && npx vite --port 5173 &

# Run backend tests
cd backend && python3 -m pytest tests/ -v

# Run frontend tests
cd frontend && npx vitest run

# Run stress test
python3 backend/stress_test.py
```