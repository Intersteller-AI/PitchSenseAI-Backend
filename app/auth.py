# app/auth.py
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import os
from fastapi import Request, HTTPException, status
from typing import Optional


load_dotenv()

print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

# Load env var if you use .env via python-dotenv in main
CRED_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
DISABLE_AUTH = os.environ.get("DISABLE_AUTH", "true").lower()  # default true for dev

_initialized = False

def init_firebase_admin():
    global _initialized
    if _initialized:
        return
    if DISABLE_AUTH == "true":
        # skip real init in dev mode
        _initialized = False
        return
    if not CRED_PATH:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set (service account JSON)")
    cred = None
    # allow passing JSON content as env var too (not recommended for long)
    if os.path.exists(CRED_PATH):
        cred = credentials.Certificate(CRED_PATH)
    else:
        # maybe CRED_PATH contains the JSON content; try parsing dict
        try:
            import json
            data = json.loads(CRED_PATH)
            cred = credentials.Certificate(data)
        except Exception:
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS must be a file path or JSON string")
    firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
    _initialized = True

def verify_id_token_optional(request: Request) -> Optional[dict]:
    """
    Returns decoded token or None if not present/invalid.
    """
    if DISABLE_AUTH == "true":
        # dev convenience — return fake user
        return {"uid": "dev-user", "email": "dev@example.com"}
    init_firebase_admin()
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    id_token = parts[1]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None

def require_auth(request: Request):
    if DISABLE_AUTH == "true":
        return {"uid": "dev-user", "email": "dev@example.com"}

    init_firebase_admin()
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        import traceback
        print("Auth error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Invalid or missing token")
