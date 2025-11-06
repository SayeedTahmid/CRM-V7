"""Minimal FastAPI CRM backend scaffold

Provides a health endpoint and a minimal customers API. This version
optionally initializes Firebase Admin (Firestore + Auth) when
`FIREBASE_CREDENTIALS_JSON` is configured. When Firestore is available
customers are stored there; otherwise the app falls back to an in-memory
store so development can continue without credentials.
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import uuid
import datetime
import os
from dotenv import load_dotenv

from services.firebase import init_firebase, get_firestore_client, verify_id_token
from api.middleware.auth import get_current_user, require_roles, get_tenant
from fastapi.staticfiles import StaticFiles

# include routers
from api.routes.logs import router as logs_router
from api.routes.complaints import router as complaints_router

load_dotenv()

REQUIRE_AUTH = os.environ.get("REQUIRE_AUTH", "false").lower() in ("1", "true", "yes")

# Try to initialize Firebase (graceful — returns None if unavailable)
firestore_client = init_firebase()

app = FastAPI(title="Codex CRM - Backend (scaffold)", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads folder for static serving
uploads_path = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")


# Pydantic models
class CustomerCreate(BaseModel):
    companyName: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = "prospect"
    assignedTo: Optional[str] = None
    tags: Optional[List[str]] = []


class Customer(CustomerCreate):
    id: str
    createdAt: datetime.datetime
    createdBy: Optional[str] = "system"


# In-memory store (used when Firestore isn't configured)
db_customers: Dict[str, Customer] = {}


def _require_auth_dependency(authorization: Optional[str] = Header(None)):
    """Dependency to optionally verify Firebase ID token when REQUIRE_AUTH is true.

    If REQUIRE_AUTH is false, returns None. If true and Authorization header is
    present, attempts to verify the token; on failure raises HTTPException(401).
    """
    if not REQUIRE_AUTH:
        return None
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = parts[1]
    try:
        decoded = verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "firestore": bool(firestore_client), "require_auth": REQUIRE_AUTH}


# Include feature routers
app.include_router(logs_router, prefix="/v1")
app.include_router(complaints_router, prefix="/v1")


@app.get("/v1/customers", response_model=List[Customer])
def list_customers(tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('viewer', 'sales_rep', 'manager', 'admin', 'super_admin'))):
    """Return customers for the tenant. If Firestore is initialized, read from it; otherwise fallback to in-memory.

    Requires at least 'viewer' role. `current_user` is provided by RBAC dependency.
    """
    if firestore_client:
        qs = firestore_client.collection("customers").where("tenant_id", "==", tenant).stream()
        out = []
        for doc in qs:
            data = doc.to_dict()
            cust = Customer(
                id=doc.id,
                companyName=data.get("companyName"),
                email=data.get("email"),
                phone=data.get("phone"),
                status=data.get("status"),
                assignedTo=data.get("assignedTo"),
                tags=data.get("tags", []),
                createdAt=data.get("createdAt"),
                createdBy=data.get("createdBy"),
            )
            out.append(cust)
        return out

    # fallback in-memory
    return [c for c in db_customers.values() if getattr(c, "tenant_id", "default") == tenant]


@app.post("/v1/customers", status_code=201, response_model=Customer)
def create_customer(payload: CustomerCreate, tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('sales_rep', 'manager', 'admin', 'super_admin'))):
    """Create customer for the tenant. Requires role: sales_rep, manager, admin, or super_admin."""
    cid = str(uuid.uuid4())
    now = datetime.datetime.utcnow()

    if firestore_client:
        doc_ref = firestore_client.collection("customers").document(cid)
        doc_data = payload.dict()
        # Firestore can't serialize datetime automatically in all contexts; store as ISO
        doc_data.update({
            "createdAt": now,
            "createdBy": current_user.get("uid") if current_user else "system",
            "tenant_id": tenant,
        })
        doc_ref.set(doc_data)
        cust = Customer(id=cid, createdAt=now, createdBy=doc_data["createdBy"], **payload.dict())
        return cust

    # fallback in-memory (store tenant_id attribute on model for filtering)
    cust = Customer(id=cid, createdAt=now, createdBy=(current_user.get("uid") or "system"), **payload.dict())
    # attach tenant info for fallback filter
    setattr(cust, "tenant_id", tenant)
    db_customers[cid] = cust
    return cust


@app.get("/v1/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str, tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('viewer', 'sales_rep', 'manager', 'admin', 'super_admin'))):
    """Get single customer; requires at least 'viewer' role and tenant matching (unless super_admin)."""
    if firestore_client:
        doc = firestore_client.collection("customers").document(customer_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Customer not found")
        data = doc.to_dict()
        if data.get("tenant_id") != tenant and current_user.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")
        return Customer(
            id=doc.id,
            companyName=data.get("companyName"),
            email=data.get("email"),
            phone=data.get("phone"),
            status=data.get("status"),
            assignedTo=data.get("assignedTo"),
            tags=data.get("tags", []),
            createdAt=data.get("createdAt"),
            createdBy=data.get("createdBy"),
        )

    cust = db_customers.get(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    if getattr(cust, "tenant_id", "default") != tenant and current_user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")
    return cust
