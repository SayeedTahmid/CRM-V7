from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List, Optional
import uuid
import datetime
import os

from api.middleware.auth import get_tenant, require_roles, get_current_user, can_modify_field
from services.firebase import get_firestore_client
from services.storage import save_upload_file

router = APIRouter()

# In-memory store for logs as fallback
db_logs = {}


@router.get("/customers/{customer_id}/logs")
def list_logs(customer_id: str, tenant: str = Depends(get_tenant), current_user: dict = Depends(require_roles('viewer', 'sales_rep', 'support', 'manager', 'admin', 'super_admin'))):
    firestore = get_firestore_client()
    if firestore:
        qs = firestore.collection("logs").where("customer_id", "==", customer_id).where("tenant_id", "==", tenant).stream()
        out = [doc.to_dict() for doc in qs]
        return out

    # fallback
    return [l for l in db_logs.values() if l.get("customer_id") == customer_id and l.get("tenant_id", "default") == tenant]


@router.post("/customers/{customer_id}/logs", status_code=201)
async def create_log(
    customer_id: str,
    type: str = Form(...),
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    tenant: str = Depends(get_tenant),
    current_user: dict = Depends(require_roles('sales_rep', 'support', 'manager', 'admin', 'super_admin')),
):
    """Create a log entry for a customer. Accepts optional file attachments."""
    now = datetime.datetime.utcnow()
    lid = str(uuid.uuid4())
    attachments = []
    if files:
        for f in files:
            meta = await save_upload_file(f, tenant=tenant)
            attachments.append(meta)

    payload = {
        "id": lid,
        "customer_id": customer_id,
        "type": type,
        "message": message,
        "attachments": attachments,
        "createdAt": now,
        "createdBy": current_user.get("uid") if current_user else "system",
        "tenant_id": tenant,
    }

    firestore = get_firestore_client()
    if firestore:
        firestore.collection("logs").document(lid).set(payload)
        return payload

    db_logs[lid] = payload
    return payload


@router.put("/logs/{log_id}")
async def update_log(log_id: str, message: Optional[str] = Form(None), current_user: dict = Depends(require_roles('sales_rep', 'support', 'manager', 'admin', 'super_admin'))):
    # Only allow updates if user is creator or admin
    firestore = get_firestore_client()
    if firestore:
        doc_ref = firestore.collection("logs").document(log_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Log not found")
        data = doc.to_dict()
        if data.get("createdBy") != current_user.get("uid") and current_user.get("role") not in ("admin", "super_admin"):
            raise HTTPException(status_code=403, detail="Forbidden: cannot edit this log")
        updates = {}
        if message is not None:
            updates["message"] = message
        if updates:
            doc_ref.update(updates)
        data.update(updates)
        return data

    item = db_logs.get(log_id)
    if not item:
        raise HTTPException(status_code=404, detail="Log not found")
    if item.get("createdBy") != current_user.get("uid") and current_user.get("role") not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Forbidden: cannot edit this log")
    if message is not None:
        item["message"] = message
    return item


@router.delete("/logs/{log_id}")
def delete_log(log_id: str, current_user: dict = Depends(require_roles('manager', 'admin', 'super_admin'))):
    firestore = get_firestore_client()
    if firestore:
        doc_ref = firestore.collection("logs").document(log_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Log not found")
        doc_ref.delete()
        return {"success": True}

    if log_id in db_logs:
        del db_logs[log_id]
        return {"success": True}
    raise HTTPException(status_code=404, detail="Log not found")
