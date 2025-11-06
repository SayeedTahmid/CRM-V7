"""Example of testing with Firebase emulator.

This shows how to write tests that use the Firebase emulator
for auth token verification and Firestore operations.
"""
import pytest
from fastapi.testclient import TestClient
import os
from main import app

# Force emulator mode for tests
os.environ["FIREBASE_EMULATOR"] = "true"
os.environ["REQUIRE_AUTH"] = "true"

client = TestClient(app)

def test_health_check():
    """Health endpoint should report emulator mode."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["firestore"] == True  # emulator should connect
    assert data["require_auth"] == True

def test_list_customers_requires_auth():
    """Endpoints should require auth token when REQUIRE_AUTH=true."""
    # No token
    response = client.get("/v1/customers")
    assert response.status_code == 401
    
    # With token (emulator accepts any token)
    response = client.get("/v1/customers", headers={
        "Authorization": "Bearer fake-token",
        "X-Tenant-ID": "default"
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_customer_with_tenant():
    """Creates a customer with tenant isolation."""
    headers = {
        "Authorization": "Bearer fake-token",
        "X-Tenant-ID": "tenant-a"
    }
    # Create in tenant-a
    response = client.post("/v1/customers", headers=headers, json={
        "companyName": "Test Co",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    customer_id = response.json()["id"]
    
    # Should appear in tenant-a list
    response = client.get("/v1/customers", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Should not appear in tenant-b list
    headers["X-Tenant-ID"] = "tenant-b"
    response = client.get("/v1/customers", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0