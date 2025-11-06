from typing import Optional, Callable, Any
from fastapi import Header, HTTPException, Depends
import os
import logging

from services.firebase import verify_id_token, get_firestore_client

DEFAULT_TENANT = os.environ.get("DEFAULT_TENANT", "default")
REQUIRE_AUTH = os.environ.get("REQUIRE_AUTH", "false").lower() in ("1", "true", "yes")


def get_tenant(x_tenant_id: Optional[str] = Header(None)) -> str:
    """Resolve tenant from X-Tenant-ID header or default."""
    return x_tenant_id or DEFAULT_TENANT


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Resolve current user from Authorization header using Firebase when enabled.

    Returns a dict with keys: uid, email, role, tenant (if present in custom claims).
    When REQUIRE_AUTH is False, returns a development super-admin user to ease local dev.
    """
    if not REQUIRE_AUTH:
        logging.debug("Auth disabled: returning dev user")
        return {"uid": "dev", "email": "dev@example.com", "role": "super_admin", "tenant": DEFAULT_TENANT}

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = parts[1]

    try:
        decoded = verify_id_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")

    # decoded token may contain custom claims (e.g., role, tenant)
    user = {
        "uid": decoded.get("uid") or decoded.get("user_id") or decoded.get("sub"),
        "email": decoded.get("email"),
        "role": decoded.get("role") or (decoded.get("claims") or {}).get("role") or "viewer",
        "tenant": decoded.get("tenant") or (decoded.get("claims") or {}).get("tenant") or DEFAULT_TENANT,
    }
    return user


def require_roles(*allowed_roles: str) -> Callable[[Any], Any]:
    """Dependency factory that ensures current user has one of the allowed roles.

    Usage in an endpoint:
        @app.post(...)
        def create(..., current_user: dict = Depends(require_roles('admin', 'manager'))):
            ...
    """

    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        role = current_user.get("role")
        if role not in allowed_roles and "super_admin" not in (role,):
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return current_user

    return dependency


def can_modify_field(role: str, module: str, field: str) -> bool:
    """Simple field-level permission matrix.

    module: e.g., 'complaint', 'log'
    field: field name being modified
    Returns True if the role can modify the field.
    """
    # Define per-module rules
    rules = {
        "complaint": {
            "status": {"support", "manager", "admin", "super_admin"},
            "assignedTo": {"manager", "admin", "super_admin"},
            # allow most roles to modify text fields
            "default": {"viewer", "sales_rep", "support", "manager", "admin", "super_admin"},
        },
        "log": {
            "default": {"viewer", "sales_rep", "support", "manager", "admin", "super_admin"},
        },
    }

    module_rules = rules.get(module, {})
    allowed = module_rules.get(field) or module_rules.get("default") or set()
    return role in allowed
