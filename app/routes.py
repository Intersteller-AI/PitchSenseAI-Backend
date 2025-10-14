# app/routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from google.cloud import firestore, pubsub_v1
import os, json
from .storage import upload_file_bytes
from .auth import require_auth

db = firestore.Client()
router = APIRouter()

PROJECT_ID = os.getenv("GCP_PROJECT")
TOPIC_ID = os.getenv("GCP_PUBSUB_TOPIC")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

class UploadResponse(BaseModel):
    analysisId: str
    status: str
    filePath: str

@router.post("/api/upload", response_model=UploadResponse, status_code=202)
async def upload(file: UploadFile = File(...), user=Depends(require_auth)):
    print(f"upload api called by {user.get('email')}")
    uid = user.get("uid") if isinstance(user, dict) else user["uid"]
    contents = await file.read()

    if file.content_type not in [
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "image/png",
        "image/jpeg",
    ]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    gcs_path, public_url = upload_file_bytes(
        uid, file.filename, contents, content_type=file.content_type
    )

    analysis_id = "analysis_" + str(uuid4())
    doc_ref = db.collection("analyses").document(analysis_id)
    doc_ref.set({
        "userId": uid,
        "fileId": gcs_path,
        "filePath": public_url,
        "status": "pending",
        "createdAt": firestore.SERVER_TIMESTAMP,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })

    message = {
        "analysisId": analysis_id,
        "bucketPath": gcs_path,
        "publicUrl": public_url,
        "contentType": file.content_type,
        "userId": uid
    }
    # publisher.publish(topic_path, json.dumps(message).encode("utf-8"))

    return {"analysisId": analysis_id, "status": "pending", "filePath": public_url}
