# Railway Deployment - Environment Variables Setup

Pada Railway Dashboard, set environment variables ini:

## Required Variables:

```
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your_strong_secret_key_here

# Server
HOST=0.0.0.0
PORT=8000

# Cloudinary
CLOUDINARY_CLOUD_NAME=dnvutggrr
CLOUDINARY_API_KEY=333844396842318
CLOUDINARY_API_SECRET=sMDLdsK7TSymn8YxjN8H8ApjIDs

# Firebase
FIREBASE_PROJECT_ID=detectbanana
FIREBASE_API_KEY=AIzaSyD6J1TWa-5l8OeAAIU6fkoAcXiovZpf2ZQ
FIREBASE_AUTH_DOMAIN=detectbanana.firebaseapp.com
FIREBASE_DATABASE_URL=https://detectbanana-default-rtdb.firebaseio.com
FIREBASE_STORAGE_BUCKET=detectbanana.firebasestorage.app
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

# Model
MODEL_PATH=trained_models/banana_detection_v1/weights/best.pt
CONFIDENCE_THRESHOLD=0.5
IOU_THRESHOLD=0.45

# Classes
CLASS_NAMES=Mentah,Matang,Busuk
```

## Untuk Firebase Service Account:

**Option 1: Paste credentials langsung**
```
FIREBASE_CREDENTIALS_JSON={paste entire JSON content here}
```

**Option 2: Upload file via Railway**
```bash
railway login
railway link
# Upload firebase-credentials.json
```

## Perhatian:

⚠️ Model file (best.pt) tidak di-upload ke git karena size besar
- Download model manual ke `trained_models/banana_detection_v1/weights/best.pt`
- Atau setup automated download saat deployment
- App akan tetap berjalan tanpa model (hanya return error saat /api/predict dipanggil)
