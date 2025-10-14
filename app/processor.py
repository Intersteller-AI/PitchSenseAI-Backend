# app/processor.py
from google.cloud import vision
from google.cloud import storage
from app.firestore_client import db
import json
import os
import subprocess

vision_client = vision.ImageAnnotatorClient()

def run_ocr_gcs(gcs_uri: str) -> str:
    """
    Run document OCR on the file at gcs_uri and return extracted text.
    gcs_uri must be like 'gs://bucket/path/to/file.pdf'
    """
    # Build image object for the vision API
    from google.cloud.vision_v1 import types
    image = vision.types.Image()
    image.source.image_uri = gcs_uri
    response = vision_client.document_text_detection(image=image)
    annotation = response.full_text_annotation
    text = ''
    if annotation:
        text = annotation.text
    return text

def call_llm_extract(ocr_text: str) -> dict:
    """
    Placeholder: call your LLM / Vertex AI here with strict prompt to return JSON.
    For now, return a mock result or parse using a simple heuristic.
    """
    # TODO: integrate Vertex AI / Gemini SDK here
    # Keep this function synchronous or create async task.
    mock = {
        "startup_info": {"name": "Demo Startup", "sector": "saas"},
        "traction": {"users": 100, "mrr": 2000},
        "financials": {"funding_raised_usd": 100000, "burn_rate_usd": 5000, "runway_months": 20},
        "benchmarks": [{"metric":"ARR","value":24000,"median":150000,"status":"Below"}],
        "risks":[{"flag":"High Churn","severity":"Medium","note":"Churn not provided","evidence":"p.6"}],
        "ai_generated_summary":{"short_summary":"Demo startup shows early traction", "recommendation":"Ask for more metrics"}
    }
    return mock

def process_analysis(analysis_id: str) -> None:
    """
    Orchestrates: download file (or use GCS path), run OCR, call LLM, store result in Firestore.
    """
    doc_ref = db.collection("analyses").document(analysis_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("analysis not found")
    data = doc.to_dict()
    file_path = data.get("filePath")  # gs://...
    # 1) OCR
    try:
        ocr_text = run_ocr_gcs(file_path)
        # 2) Call LLM (Vertex AI) to extract structured JSON
        result = call_llm_extract(ocr_text)
        # 3) Save result to Firestore
        doc_ref.update({
            "status": "done",
            "result": result,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        doc_ref.update({"status": "error", "error": str(e)})
        raise
