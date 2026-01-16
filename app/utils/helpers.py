"""
Helper functions
Utility functions yang digunakan di berbagai tempat
"""

import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid
from datetime import datetime

def allowed_file(filename):
    """
    Check apakah file extension diperbolehkan
    """
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file):
    """
    Save uploaded file ke folder uploads dengan nama unik
    """
    original_filename = secure_filename(file.filename)
    file_ext = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    return filepath

def format_detection_response(detections, image_url=None, metadata=None):
    """
    Format detection results menjadi response JSON yang konsisten
    """
    return {
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'image_url': image_url,
        'detections': detections,
        'metadata': metadata or {}
    }

def calculate_confidence_level(confidence):
    """
    Convert confidence score ke level (Low/Medium/High)
    """
    if confidence >= 0.8:
        return 'High'
    elif confidence >= 0.6:
        return 'Medium'
    else:
        return 'Low'
    