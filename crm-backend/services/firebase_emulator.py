"""Firebase emulator integration helper for local development.

This module provides a consistent way to initialize firebase-admin
to use local emulators. It reads FIREBASE_EMULATOR=true from env
to switch to emulator mode.

Usage:
    1. Start emulators: firebase emulators:start
    2. Set env var: FIREBASE_EMULATOR=true
    3. Run your FastAPI app normally
"""
import os
from typing import Optional
import logging

# Emulator host defaults (matches firebase.json)
AUTH_EMULATOR_HOST = "localhost:9099"
FIRESTORE_EMULATOR_HOST = "localhost:8080"
STORAGE_EMULATOR_HOST = "localhost:9199"

def init_firebase_with_emulator():
    """Initialize firebase-admin SDK to use local emulators.
    
    Returns the initialized Firestore client or None if firebase-admin
    import fails.
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Tell firebase-admin to use emulators
        os.environ["FIRESTORE_EMULATOR_HOST"] = FIRESTORE_EMULATOR_HOST
        os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = AUTH_EMULATOR_HOST
        
        # Use a fake cert - emulator doesn't validate it
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": "demo-project",
            "private_key": "fake-key",
            "client_email": "fake@example.com",
        })
        
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        logging.info("Initialized Firebase with emulator")
        return db
    except Exception as e:
        logging.warning(f"Could not initialize Firebase emulator: {e}")
        return None

def init_firebase_auto():
    """Initialize Firebase based on FIREBASE_EMULATOR env var.
    
    If FIREBASE_EMULATOR=true, uses emulator.
    Otherwise tries normal initialization with service account.
    """
    use_emulator = os.environ.get("FIREBASE_EMULATOR", "").lower() in ("1", "true", "yes")
    if use_emulator:
        return init_firebase_with_emulator()
        
    # Fall back to normal initialization
    from services.firebase import init_firebase
    return init_firebase()