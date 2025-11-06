# Firebase Emulator Setup

This document explains how to run the CRM locally using Firebase Emulators for Auth and Firestore. This lets you develop without real Firebase credentials.

## Prerequisites

1. Install Node.js and npm (for Firebase CLI)
2. Install Firebase CLI globally:
```bash
npm install -g firebase-tools
```

3. Install backend dependencies (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\crm-backend\requirements.txt
```

4. Install frontend dependencies:
```powershell
cd .\crm-frontend
npm install
```

## Running the Stack

1. Start Firebase Emulators (from project root):
```powershell
firebase emulators:start
```
This starts:
- Auth emulator on port 9099
- Firestore emulator on port 8080
- Storage emulator on port 9199
- Emulator UI on http://localhost:4000

2. Start the backend (new terminal):
```powershell
# Copy example env
Copy-Item .\crm-backend\.env.local .\.env
# Start server
.\.venv\Scripts\Activate.ps1
python -m uvicorn crm-backend.main:app --reload --port 8000
```

3. Start the frontend (new terminal):
```powershell
cd .\crm-frontend
# Copy example env
Copy-Item .\.env.local .\.env
# Start dev server
npm run dev
```

## Using the Emulated Stack

1. Open http://localhost:4000 for Firebase Emulator UI
   - Monitor Auth users, Firestore data
   - Create test users

2. Open http://localhost:5173 for the CRM frontend
   - Login with any email/password (emulator accepts all)
   - Backend will receive valid Firebase ID tokens

3. Create test data:
   - POST http://localhost:8000/v1/customers
   - Header: Authorization: Bearer any-token
   - Header: X-Tenant-ID: default
   - Body: {"companyName": "Test Co"}

## Switching to Real Firebase

1. Get your Firebase project config:
   - Update `crm-frontend/src/firebase-config.js`
   - Download service account JSON

2. Update environment:
   - Backend: Set FIREBASE_EMULATOR=false and FIREBASE_CREDENTIALS_JSON
   - Frontend: Set VITE_USE_FIREBASE_EMULATOR=false

## Notes

- Emulator data is ephemeral (cleared on restart)
- Auth emulator accepts any email/password
- You can use the Emulator UI to create test data
- Real Firebase config is easy to switch with env vars