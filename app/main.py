# app/main.py
import os
from fastapi import FastAPI, Depends
from app.auth import require_auth, verify_id_token_optional, init_firebase_admin
from pydantic import BaseModel
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from uuid import uuid4
from app.storage import upload_file_bytes
from app.firestore_client import db
from app.models import UploadResponse
from google.cloud import firestore
from app import processor
# app/main.py
from fastapi import FastAPI
from .routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

# load .env if present
load_dotenv()

app = FastAPI(title="PitchSense AI Backend")

# Allow requests from frontend
origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "https://pitchsenseai.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],   # allow all headers
)

# simple health
@app.get("/health")
def health():
    return {"status": "ok"}

# test endpoint that accepts optional token
@app.get("/api/auth/verify")
def verify_optional(request_user = Depends(verify_id_token_optional)):
    if request_user:
        return {"authenticated": True, "user": request_user}
    return {"authenticated": False}

# endpoint requiring auth
@app.get("/api/auth/test")
def auth_test(user = Depends(require_auth)):
    # user is decoded token dict containing uid & email (or dev-user)
    return {"ok": True, "uid": user.get("uid"), "email": user.get("email")}

# start-up helper to initialize firebase in non-dev mode
@app.on_event("startup")
def startup_event():
    # only initialize if DISABLE_AUTH != 'true'
    if os.environ.get("DISABLE_AUTH", "true").lower() != "true":
        init_firebase_admin()

# include all routes from routes.py
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "PitchSense AI backend is running 🚀"}
        

@app.get("/api/analysis/{analysis_id}")
def get_analysis(analysis_id: str, user=Depends(require_auth)):
    doc_ref = db.collection("analyses").document(analysis_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Not found")
    data = doc.to_dict()
    # permission check
    uid = user.get("uid") if isinstance(user, dict) else user["uid"]
    if data.get("userId") != uid and os.environ.get("DISABLE_AUTH","false")!="true":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"analysisId": analysis_id, "status": data.get("status"), "result": data.get("result"), "updatedAt": data.get("updatedAt")}
