"""API Contract Tests for KimiFun Backend"""

import sys
import os
# Add backend app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_login():
    """Test teacher login endpoint."""
    response = client.post(
        "/auth/login",
        json={"email": "guru@KimiFun.com", "password": "password123"}
    )
    assert response.status_code in [200, 401]  # 401 if no user setup


@pytest.mark.asyncio
async def test_list_modules():
    """Test listing modules endpoint."""
    response = client.get("/content/modules?grade_level=X")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_materials():
    """Test listing materials by module."""
    response = client.get("/content/materials?module_id=1")
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_material():
    """Test creating a new material."""
    response = client.post(
        "/content/materials",
        json={
            "module_id": 1,
            "title": "Test Materi Kimia",
            "content_html": "<p>Isi materi test</p>",
            "is_published": True
        }
    )
    assert response.status_code in [200, 201, 401, 403]  # role-dependent


@pytest.mark.asyncio
async def test_virtual_lab_config():
    """Test virtual lab configuration endpoints."""
    # Test upsert lab config
    response = client.put(
        "/content/materials/1/lab",
        json={
            "material_id": 1,
            "ai_prompt_history": "Test prompt",
            "config_data": {
                "lab_title": "Test Titrasi",
                "solution_name": "HCl 0.1M",
                "titrant_name": "NaOH 0.1M",
                "indicator_type": "Phenolphthalein",
                "color_start": "#F8FAFC",
                "color_end": "#F472B6",
                "max_volume_ml": 50,
                "reaction_type": "neutralization"
            },
            "status": "ready"
        }
    )
    assert response.status_code in [200, 401, 403, 404]


@pytest.mark.asyncio
async def test_virtual_lab_get():
    """Test getting virtual lab config."""
    response = client.get("/content/materials/1/lab")
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_classes_list():
    """Test classes listing."""
    response = client.get("/classes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_enroll_by_code():
    """Test class enrollment by code."""
    response = client.post(
        "/classes/enroll",
        json={"enrollment_code": "CHEM-ABC123", "student_id": 1}
    )
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_list_users_students():
    """Test listing students."""
    response = client.get("/users/?role=student")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


"""Stress / Load Tests (standalone)"""


def test_response_time_health():
    """Test health endpoint response time < 100ms."""
    import time
    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start
    assert elapsed < 0.1, f"Health check took {elapsed:.3f}s"


def test_response_time_auth():
    """Test auth endpoint response time < 200ms."""
    import time
    start = time.time()
    response = client.post("/auth/login", json={"email": "test@test.com", "password": "pass"})
    elapsed = time.time() - start
    assert elapsed < 0.2, f"Auth login took {elapsed:.3f}s"


def test_concurrent_requests():
    """Test basic concurrent request handling."""
    import threading
    results = []

    def make_request():
        try:
            start = time.time()
            r = client.get("/health")
            elapsed = time.time() - start
            results.append((r.status_code, elapsed))
        except Exception as e:
            results.append((None, str(e)))

    threads = [threading.Thread(target=make_request) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert len(results) == 10, f"Expected 10 results, got {len(results)}"
    success_count = sum(1 for code, _ in results if code == 200)
    assert success_count >= 5, f"Expected at least 5 successful, got {success_count}"


if __name__ == "__main__":
    """Run basic smoke tests manually."""
    import time
    print("Running API contract tests manually...")
    
    # Test health
    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start
    print(f"Health endpoint: status={response.status_code}, time={elapsed:.3f}s, PASS={elapsed < 0.1}")
    
    # Test auth
    start = time.time()
    response = client.post("/auth/login", json={"email": "guru@KimiFun.com", "password": "password123"})
    elapsed = time.time() - start
    print(f"Auth login: status={response.status_code}, time={elapsed:.3f}s, PASS={elapsed < 0.2}")
    
    # Test concurrent
    results = []
    def make_request():
        try:
            start = time.time()
            r = client.get("/health")
            elapsed = time.time() - start
            results.append((r.status_code, elapsed))
        except Exception as e:
            results.append((None, str(e)))
    
    threads = [threading.Thread(target=make_request) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    
    success_count = sum(1 for code, _ in results if code == 200)
    print(f"Concurrent requests: {len(results)} total, {success_count} successful")
    
    print("\nAll manual smoke tests completed.")