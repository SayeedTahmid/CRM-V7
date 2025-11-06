"""Firebase Admin wrapper for optional Firestore and Auth usage.

This module initializes firebase-admin when credentials are available and
exposes helper functions used by the FastAPI app.

If no credentials are configured, functions will return None or raise
informative errors. The main app uses graceful fallback to an in-memory
store when Firestore isn't initialized.
"""
from typing import Optional
import os
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
except Exception:
    firebase_admin = None
    credentials = None
    auth = None
    firestore = None

_app = None
_client = None


def init_firebase():
    """Attempt to initialize firebase-admin using FIREBASE_CREDENTIALS_JSON env var.

    Returns a Firestore client instance on success, or None on failure.
    """
    global _app, _client
    if firebase_admin is None:
        logging.info("firebase_admin not installed or failed to import")
        return None

    cred_path = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    try:
        if cred_path:
            cred = credentials.Certificate(cred_path)
            _app = firebase_admin.initialize_app(cred)
        else:
            # try default credentials
            _app = firebase_admin.initialize_app()

        _client = firestore.client()
        logging.info("Initialized firebase-admin and Firestore client")
        return _client
    except Exception as e:
        logging.warning(f"Could not initialize firebase-admin: {e}")
        _app = None
        _client = None
        return None


def get_firestore_client():
    return _client


def verify_id_token(id_token: str) -> Optional[dict]:
    """Verify Firebase ID token and return decoded token (dict) or raise.

    Raises Exception if verification fails.
    """
    if auth is None:
        raise RuntimeError("firebase_admin.auth is not available")

    return auth.verify_id_token(id_token)
