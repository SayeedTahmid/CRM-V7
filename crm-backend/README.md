# crm-backend — Minimal FastAPI scaffold

This is a minimal FastAPI scaffold to get started with the CRM backend.

Prereqs:
- Python 3.10+
- (optional) virtualenv / venv

Install and run (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -r requirements.txt
# Run the server
python -m uvicorn main:app --reload --port 8000
```

Endpoints:
- GET /health — health check
- GET /v1/customers — list customers (in-memory)
- POST /v1/customers — create a customer (in-memory)
- GET /v1/customers/{id} — get single customer

This is intentionally simple so we can iterate fast. Next: wire Firestore (or Postgres), add Firebase Auth middleware, then implement logs, complaints and RBAC.
