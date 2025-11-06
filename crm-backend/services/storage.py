"""Simple local file storage helper for uploads.

In production, swap this with Cloud Storage (GCS/AWS S3) integration. The
helpers return metadata that can be stored in Firestore along with the
parent resource (log or complaint).
"""
from typing import Dict
import os
import uuid
import aiofiles

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
BASE_DIR = os.path.abspath(BASE_DIR)

os.makedirs(BASE_DIR, exist_ok=True)


async def save_upload_file(file, tenant: str = "default") -> Dict:
    """Save a Starlette UploadFile to disk under uploads/<tenant>/ and return metadata."""
    tenant_dir = os.path.join(BASE_DIR, tenant)
    os.makedirs(tenant_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(tenant_dir, filename)

    size = 0
    async with aiofiles.open(path, 'wb') as out_file:
        while True:
            chunk = await file.read(1024 * 64)
            if not chunk:
                break
            size += len(chunk)
            await out_file.write(chunk)

    # Return metadata
    return {
        "original_name": file.filename,
        "stored_name": filename,
        "content_type": file.content_type,
        "size": size,
        "url": f"/uploads/{tenant}/{filename}",
    }
