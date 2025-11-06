from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List, Optional
import uuid
import datetime

from api.middleware.auth import get_tenant, require_roles, get_current_user, can_modify_field
from services.firebase import get_firestore_client
from services.storage import save_upload_file

router = APIRouter()

# In-memory store fallback
db_complaints = {}


@router.get("/complaints")
def list_complaints(tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('viewer', 'support', 'manager', 'admin', 'super_admin'))):
    firestore = get_firestore_client()
    if firestore:
        qs = firestore.collection("complaints").where("tenant_id", "==", tenant).stream()
        return [doc.to_dict() for doc in qs]
    return [c for c in db_complaints.values() if c.get("tenant_id", "default") == tenant]


@router.post("/complaints", status_code=201)
async def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    customerId: str = Form(...),
    severity: str = Form("medium"),
    files: Optional[List[UploadFile]] = File(None),
    tenant: str = Depends(get_tenant),
    current_user: dict = Depends(require_roles('support', 'sales_rep', 'manager', 'admin', 'super_admin')),
):
    now = datetime.datetime.utcnow()
    cid = str(uuid.uuid4())
    attachments = []
    if files:
        for f in files:
            meta = await save_upload_file(f, tenant=tenant)
            attachments.append(meta)

    payload = {
        "id": cid,
        "title": title,
        "description": description,
        "customerId": customerId,
        "severity": severity,
        "status": "new",
        "attachments": attachments,
        "createdAt": now,
        "createdBy": current_user.get("uid") if current_user else "system",
        "tenant_id": tenant,
    }

    firestore = get_firestore_client()
    if firestore:
        firestore.collection("complaints").document(cid).set(payload)
        return payload

    db_complaints[cid] = payload
    return payload


@router.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str, tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('viewer', 'support', 'manager', 'admin', 'super_admin'))):
    firestore = get_firestore_client()
    if firestore:
        doc = firestore.collection("complaints").document(complaint_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Complaint not found")
        data = doc.to_dict()
        if data.get("tenant_id") != tenant and current_user.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")
        return data

    item = db_complaints.get(complaint_id)
    if not item:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if item.get("tenant_id", "default") != tenant and current_user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")
    return item


@router.put("/complaints/{complaint_id}/status")
def update_complaint_status(complaint_id: str, status: str = Form(...), tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('support', 'manager', 'admin', 'super_admin'))):
    # Only specific roles can update status
    if not can_modify_field(current_user.get("role"), "complaint", "status"):
        raise HTTPException(status_code=403, detail="Forbidden: cannot change status")

    firestore = get_firestore_client()
    if firestore:
        doc_ref = firestore.collection("complaints").document(complaint_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Complaint not found")
        doc_ref.update({"status": status})
        data = doc_ref.get().to_dict()
        return data

    item = db_complaints.get(complaint_id)
    if not item:
        raise HTTPException(status_code=404, detail="Complaint not found")
    item["status"] = status
    return item


@router.post("/complaints/{complaint_id}/comments")
def add_internal_comment(complaint_id: str, comment: str = Form(...), tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('support', 'manager', 'admin', 'super_admin'))):
    firestore = get_firestore_client()
    note = {
        "id": str(uuid.uuid4()),
        "comment": comment,
        "createdAt": datetime.datetime.utcnow(),
        "createdBy": current_user.get("uid"),
    }
    if firestore:
        doc_ref = firestore.collection("complaints").document(complaint_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Complaint not found")
        data = doc.to_dict()
        comments = data.get("internalComments", [])
        comments.append(note)
        doc_ref.update({"internalComments": comments})
        data = doc_ref.get().to_dict()
        return data

    item = db_complaints.get(complaint_id)
    if not item:
        raise HTTPException(status_code=404, detail="Complaint not found")
    item.setdefault("internalComments", []).append(note)
    return item
