# app/storage.py
import os
from google.cloud import storage

BUCKET = os.environ.get("GCLOUD_STORAGE_BUCKET")
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET)

def upload_file_bytes(user_id: str, filename: str, file_bytes: bytes, content_type: str = None) -> tuple[str, str]:
    from time import time
    path = f"uploads/{user_id}/{int(time())}-{filename}"
    blob = bucket.blob(path)

    # 👇 preserve original content type
    blob.upload_from_string(file_bytes, content_type=content_type or "application/octet-stream")

    # 👇 make it public immediately
    blob.make_public()

    public_url = f"https://storage.googleapis.com/{bucket.name}/{path}"
    return path, public_url
