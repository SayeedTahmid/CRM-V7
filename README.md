# Codex CRM — Initial Scaffold

This workspace contains an initial scaffold for the CRM described in the attached PRD. It includes:

- `crm-backend` — minimal FastAPI backend with health and customer endpoints (in-memory store)
- `crm-frontend` — minimal React scaffold (no build steps pre-installed)
- `crm-mobile` — placeholder for Kotlin Android app

What I created as a starting point:

- Minimal backend API you can run locally with Uvicorn
- Simple frontend skeleton you can expand
- A todo list recorded in the workspace to track next steps

Next steps (recommended): implement Firebase integration, authentication, persistent DB (Firestore), implement logs/complaints endpoints, wire up frontend, add tests and CI.

See `crm-backend/README.md` for instructions to run the backend locally.
