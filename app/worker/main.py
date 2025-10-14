# worker/main.py
import base64
import json
from google.cloud import firestore, storage, vision
from vertexai.preview.language_models import TextGenerationModel

db = firestore.Client()
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()

def process_pitch(event, context):
    """Triggered by Pub/Sub message."""
    message = json.loads(base64.b64decode(event['data']).decode("utf-8"))
    analysis_id = message["analysisId"]
    gcs_path = message["bucketPath"]
    content_type = message["contentType"]

    # 1️⃣ Extract text from file
    text_content = extract_text_from_gcs(gcs_path, content_type)

    # 2️⃣ Summarize with Vertex AI
    summary = run_vertex_summary(text_content)

    # 3️⃣ Save back to Firestore
    doc_ref = db.collection("analyses").document(analysis_id)
    doc_ref.update({
        "status": "completed",
        "summary": summary,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })


def extract_text_from_gcs(gcs_path, content_type):
    bucket_name, blob_name = gcs_path.split("/", 1)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if "pdf" in content_type or "ppt" in content_type:
        # Simplified → you can use Vision API's document_text_detection
        image = vision.Image(source=vision.ImageSource(gcs_image_uri=f"gs://{bucket_name}/{blob_name}"))
        response = vision_client(image=image)
        return response.full_text_annotation.text
    else:
        return blob.download_as_text()


def run_vertex_summary(text: str) -> str:
    model = TextGenerationModel.from_pretrained("gemini-1.5-pro")
    prompt = f"Summarize this pitch deck for investors:\n\n{text}"
    response = model.predict(prompt, max_output_tokens=1024)
    return response.text
