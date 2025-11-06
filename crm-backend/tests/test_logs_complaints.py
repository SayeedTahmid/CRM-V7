"""Unit tests for logs and complaints endpoints with RBAC validation.

Tests cover:
1. Log creation and retrieval with tenant isolation
2. Complaint lifecycle with attachment handling
3. RBAC permission enforcement for different roles
4. Field-level access control
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import os
import io

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configure test environment."""
    os.environ["FIREBASE_EMULATOR"] = "true"
    os.environ["REQUIRE_AUTH"] = "true"
    yield
    # Cleanup after tests

@pytest.fixture
def admin_headers():
    """Admin user in default tenant."""
    return {
        "Authorization": "Bearer admin-token",
        "X-Tenant-ID": "default"
    }

@pytest.fixture
def manager_headers():
    """Manager user in tenant-a."""
    return {
        "Authorization": "Bearer manager-token",
        "X-Tenant-ID": "tenant-a"
    }

@pytest.fixture
def user_headers():
    """Regular user in tenant-a."""
    return {
        "Authorization": "Bearer user-token",
        "X-Tenant-ID": "tenant-a"
    }

def test_create_log():
    """Test log creation with different roles."""
    headers = manager_headers()
    
    # Managers can create logs
    response = client.post("/v1/logs", headers=headers, json={
        "customerId": "123",
        "type": "CALL",
        "description": "Test call log"
    })
    assert response.status_code == 201
    log_id = response.json()["id"]
    
    # Verify log was created
    response = client.get(f"/v1/logs/{log_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == "Test call log"
    
    # Users without manager role cannot create logs
    headers = user_headers()
    response = client.post("/v1/logs", headers=headers, json={
        "customerId": "123",
        "type": "CALL", 
        "description": "Should fail"
    })
    assert response.status_code == 403

def test_list_logs_tenant_isolation():
    """Test that logs are isolated by tenant."""
    # Create log in tenant-a
    headers = manager_headers()
    response = client.post("/v1/logs", headers=headers, json={
        "customerId": "123",
        "type": "EMAIL",
        "description": "Test email log"
    })
    assert response.status_code == 201
    
    # Should appear in tenant-a list
    response = client.get("/v1/logs", headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0
    
    # Should not appear in tenant-b list
    headers["X-Tenant-ID"] = "tenant-b"
    response = client.get("/v1/logs", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_create_complaint():
    """Test complaint creation with attachment."""
    headers = user_headers()
    
    # Create complaint with attachment
    files = {
        "file": ("test.txt", io.BytesIO(b"test content"), "text/plain")
    }
    response = client.post(
        "/v1/complaints",
        headers=headers,
        data={
            "customerId": "123",
            "title": "Test Complaint",
            "description": "Test description",
            "priority": "LOW"
        },
        files=files
    )
    assert response.status_code == 201
    complaint_id = response.json()["id"]
    
    # Verify complaint was created
    response = client.get(f"/v1/complaints/{complaint_id}", headers=headers)
    assert response.status_code == 200
    complaint = response.json()
    assert complaint["title"] == "Test Complaint"
    assert "attachmentUrl" in complaint

def test_update_complaint_status_rbac():
    """Test that only admins/managers can update complaint status."""
    # Create complaint as user
    headers = user_headers()
    response = client.post("/v1/complaints", headers=headers, json={
        "customerId": "123",
        "title": "Status Test",
        "description": "Testing status updates",
        "priority": "MEDIUM"
    })
    assert response.status_code == 201
    complaint_id = response.json()["id"]
    
    # User cannot update status
    response = client.patch(f"/v1/complaints/{complaint_id}", headers=headers, json={
        "status": "RESOLVED"
    })
    assert response.status_code == 403
    
    # Manager can update status
    headers = manager_headers()
    response = client.patch(f"/v1/complaints/{complaint_id}", headers=headers, json={
        "status": "IN_PROGRESS"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"

def test_complaint_field_level_permissions():
    """Test field-level RBAC for complaints."""
    headers = user_headers()
    
    # Create complaint
    response = client.post("/v1/complaints", headers=headers, json={
        "customerId": "123",
        "title": "Field Test",
        "description": "Testing field permissions",
        "priority": "HIGH"
    })
    assert response.status_code == 201
    complaint_id = response.json()["id"]
    
    # Users can update description
    response = client.patch(f"/v1/complaints/{complaint_id}", headers=headers, json={
        "description": "Updated description"
    })
    assert response.status_code == 200
    
    # Users cannot update internal notes
    response = client.patch(f"/v1/complaints/{complaint_id}", headers=headers, json={
        "internalNotes": "Should fail"
    })
    assert response.status_code == 403
    
    # Managers can update internal notes
    headers = manager_headers()
    response = client.patch(f"/v1/complaints/{complaint_id}", headers=headers, json={
        "internalNotes": "Internal update"
    })
    assert response.status_code == 200