# app/firestore_client.py
from google.cloud import firestore

# Firestore client will use GOOGLE_APPLICATION_CREDENTIALS env var
db = firestore.Client()
