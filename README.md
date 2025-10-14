# PitchSense Backend

This is the backend service for **PitchSense**, built with **FastAPI**. It powers the hackathon MVP by handling authentication, file uploads, and AI-driven analysis workflows using Firebase, Firestore, and Google Cloud Storage.

---

## 🎯 Overview

PitchSense Backend is the core service powering the **Founder → Investor flow**:
- Handles authentication (via Firebase)
- Stores pitch decks securely
- Queues & processes analysis jobs
- Serves AI-generated insights to the frontend dashboard

---

## 🚀 Features

* **Health Check** endpoint for monitoring service availability.
* **Authentication** with Firebase (required and optional modes).
* **File Uploads** with support for PDF, PPT, PPTX, PNG, and JPEG.
* **Analysis Management**: Uploads are stored in Firestore with status tracking.
* **Inline or Async Processing**: Uploads can be processed immediately or queued.

---

## 🔄 Workflow (High Level)

Founder → Upload Pitch Deck → Backend Stores & Triggers AI → AI Processes File → Insights Saved in DB → Investor Dashboard Displays Results

*(See diagram.png in repo for visual representation)*

![PitchSense Architecture](https://firebasestorage.googleapis.com/v0/b/pitchsense-ai.firebasestorage.app/o/IMG-20250919-WA0006.jpg?alt=media&token=65d922db-c2a8-40ef-892e-86d92da17158)

---

## 🛠️ Tech Stack

* [FastAPI](https://fastapi.tiangolo.com/) – API framework
* [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup) – Authentication
* [Google Firestore](https://cloud.google.com/firestore) – Database
* [Google Cloud Storage](https://cloud.google.com/storage) – File storage
* [Python 3.10+](https://www.python.org/)

---

## 📦 Setup & Installation

### Prerequisites

* Python 3.10+
* Firebase project credentials (`pitchesense-ai-keys.json`)
* Google Cloud project with Firestore + Storage enabled
* `.env` file with required environment variables

### Installation

```bash
# clone repository
git clone https://github.com/your-org/pitchesense-backend.git
cd pitchesense-backend

# create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --reload
```

Server will be available at:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔑 API Endpoints

### 1. Health Check

`GET /health`

Returns service status.

```json
{ "status": "ok" }
```

---

### 2. Auth Verification (Optional Token)

`GET /api/auth/verify-optional`

* ✅ Works with or without token.

**Response (unauthenticated):**

```json
{ "authenticated": false }
```

**Response (authenticated):**

```json
{
  "authenticated": true,
  "user": {
    "uid": "user123",
    "email": "test@example.com"
  }
}
```

---

### 3. Auth Test (Requires Token)

`GET /api/auth/test`

* 🔒 Requires valid Firebase token.

**Response:**

```json
{
  "ok": true,
  "uid": "user123",
  "email": "test@example.com"
}
```

---

### 4. File Upload

`POST /api/upload`

* 🔒 Requires authentication
* Accepts: PDF, PPT, PPTX, PNG, JPEG

**Response:**

```json
{
  "analysisId": "analysis_12345",
  "status": "pending",
  "filePath": "gs://bucket/uploads/user123/file.pdf"
}
```

---

### 5. Get Analysis

`GET /api/analysis/{analysis_id}`

* 🔒 Requires authentication (unless `DISABLE_AUTH=true`)

**Response (success):**

```json
{
  "analysisId": "analysis_12345",
  "status": "completed",
  "result": {...},
  "updatedAt": "2025-09-15T12:34:56Z"
}
```

**Response (not found):**

```json
{ "detail": "Not found" }
```

---

## 📌 Example Usage

### Upload a file

```bash
curl -X POST http://127.0.0.1:8000/api/upload \
     -H "Authorization: Bearer <FIREBASE_TOKEN>" \
     -F "file=@sample_pitch.pdf"
```

### Get analysis result

```bash
curl http://127.0.0.1:8000/api/analysis/analysis_12345 \
     -H "Authorization: Bearer <FIREBASE_TOKEN>"
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```ini
DISABLE_AUTH=false
GOOGLE_APPLICATION_CREDENTIALS=./pitchesense-ai-keys.json
```

---

## 📂 Project Structure

```
app/
 ├── __init__.py
 ├── auth.py              # Auth utilities (Firebase)
 ├── firestore_client.py   # Firestore client
 ├── main.py               # API entrypoint
 ├── models.py             # Pydantic models
 ├── processor.py          # File/analysis processor
 ├── storage.py            # GCS upload helpers
samples/
 ├── .env
 └── pitchesense-ai-keys.json
requirements.txt
```

---

## ☁️ Deployment

### Local Development
- Run with `uvicorn app.main:app --reload`

### Google Cloud Run
```bash
docker build -t pitchesense-backend .
gcloud run deploy pitchesense-backend --source .
```

---

## ✅ Development Notes

* Use `DISABLE_AUTH=true` for local testing (disables Firebase auth).
* Processing is inline for now (blocking). For production, switch to **Pub/Sub or Cloud Tasks** for async jobs.
* Firestore stores each analysis with:

  * `userId`
  * `fileId`
  * `filePath`
  * `status`
  * `createdAt`
  * `updatedAt`

---

## 🤝 Contributing

- Fork repo → create feature branch → open PR
- Follow commit style: `feat:`, `fix:`, `docs:`
- Run `black .` before committing (for formatting)

---

## 🚧 Future Improvements

- Switch to async analysis pipeline (Pub/Sub, Cloud Tasks)
- Add AI benchmarking + risk flagging modules
- Enhance role-based auth (Founder vs Investor)
- Add WebSocket/Realtime updates to dashboard
