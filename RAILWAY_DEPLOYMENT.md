# Railway Deployment Checklist

## ✅ Files Updated untuk Railway:

### 1. **requirements.txt**
- ✅ Downgrade: torch 2.1.2 → 2.0.1 (lebih stabil & ringan)
- ✅ Downgrade: torchvision 0.16.2 → 0.15.2 (match torch version)
- ✅ Downgrade: numpy 1.26.4 → 1.24.3 (compatibility)
- ✅ Downgrade: Pillow 12.1.0 → 10.0.0 (production standard)
- ✅ Change: opencv-python → **opencv-python-headless** (no GUI for server)
- ✅ Keep: ultralytics==8.0.147 (stable YOLOv5)
- ✅ Add: gunicorn==21.2.0 (production WSGI server)

### 2. **Procfile** (NEW)
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT run:app
```
- Tells Railway how to run the app
- 4 workers untuk concurrent requests
- Dynamic PORT dari Railway

### 3. **runtime.txt** (NEW)
```
3.11.0
```
- Specify Python version untuk Railway
- Python 3.11 adalah stable & widely supported

---

## 🚀 Deploy ke Railway:

### Step 1: Push ke GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Connect Railway
1. Buka https://railway.app
2. Login dengan GitHub
3. Klik "New Project"
4. Select "Deploy from GitHub repo"
5. Pilih repository banana-detection-backend
6. Railway otomatis detect Procfile & install dependencies

### Step 3: Environment Variables
Di Railway Dashboard, setup:
```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your_secret_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
FIREBASE_DATABASE_URL=https://detectbanana.firebaseio.com
```

### Step 4: Upload firebase-credentials.json
```bash
# Add to .gitignore (jangan commit ke GitHub)
firebase-credentials.json

# Upload ke Railway via:
1. Railway Dashboard → Variables
2. Atau upload file via Railway CLI
```

### Step 5: Deploy
- Railway otomatis build & deploy setelah push
- Check logs: Railway Dashboard → Logs
- Public URL akan diberikan

---

## ✅ Perubahan Penting:

| Aspek | Change | Reason |
|-------|--------|--------|
| OpenCV | regular → **headless** | Server tidak perlu GUI |
| PyTorch | 2.1.2 → **2.0.1** | Lebih stabil, size lebih kecil |
| TorchVision | 0.16.2 → **0.15.2** | Match PyTorch version |
| NumPy | 1.26.4 → **1.24.3** | Better compatibility |
| Pillow | 12.1.0 → **10.0.0** | Production stable |
| Server | Flask → **gunicorn** | Handle concurrent requests |

---

## 🔍 Verifikasi Local Sebelum Deploy:

```bash
# Test dengan Gunicorn locally
gunicorn -w 4 -b 127.0.0.1:5000 run:app

# Atau set environment variable
$env:PORT='5000'
gunicorn -w 4 -b 0.0.0.0:$env:PORT run:app
```

---

## 📝 .gitignore Update (PENTING!):

```
# Environment & Credentials
.env
firebase-credentials.json
firebase-*.json

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Local files
uploads/
*.log
.DS_Store

# IDE
.vscode/
.idea/
*.swp

# Railway
.railway/
```

---

## 🎯 Final Checklist:

- ✅ requirements.txt updated dengan versions stable
- ✅ Procfile dibuat untuk Railway
- ✅ runtime.txt specify Python 3.11
- ✅ firebase-credentials.json tidak di-track (add to .gitignore)
- ✅ Environment variables prepared
- ✅ .env file tidak di-commit
- ✅ All dependencies compatible

**Sekarang siap untuk deploy ke Railway!** 🚀
