"""
API Routes/Endpoints - UPDATED with Detection
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.utils.helpers import allowed_file, save_uploaded_file, format_detection_response
from app.models.yolov5_model import get_detector
from app.services.image_processor import ImageProcessor
from app.services.cloudinary_service import CloudinaryService
from app.services.firebase_service import FirebaseService
from datetime import datetime
import os
import base64

# Create Blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is working!',
        'endpoints': {
            'test': '/api/test',
            'predict': '/api/predict (POST)',
            'detect_live': '/api/detect-live (POST)'
        }
    }), 200

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint 1: Upload & Detect (Image from Gallery)
    
    Request: multipart/form-data
    - image: file (jpg/jpeg/png)
    - save: boolean (optional, default=false)
    
    Response: Detailed JSON with detection results
    """
    
    # Check if image file is in request
    if 'image' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No image file provided'
        }), 400
    
    file = request.files['image']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No selected file'
        }), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': 'Invalid file type. Allowed: jpg, jpeg, png'
        }), 400
    
    filepath = None
    
    try:
        # Save uploaded file temporarily
        filepath = save_uploaded_file(file)
        
        # Read image bytes
        with open(filepath, 'rb') as f:
            image_bytes = f.read()
        
        # Preprocess image
        image = ImageProcessor.preprocess_for_detection(image_bytes)
        
        # Get detector instance
        detector = get_detector()
        
        # Run detection
        detection_result = detector.detect(image, img_size=640)
        
        # Check if should save
        should_save = request.form.get('save', 'false').lower() == 'true'
        
        image_url = None
        firebase_doc_id = None
        
        if should_save:
            # Upload to Cloudinary
            cloudinary_result = CloudinaryService.upload_image(filepath)
            
            if cloudinary_result['success']:
                image_url = cloudinary_result['url']
                
                # Save to Firebase
                firebase_data = {
                    'image_url': image_url,
                    'detections': detection_result['detections'],
                    'inference_time': detection_result['inference_time'],
                    'source': 'upload',
                    'filename': file.filename
                }
                
                firebase_result = FirebaseService.save_detection(firebase_data)
                
                if firebase_result['success']:
                    firebase_doc_id = firebase_result['doc_id']
        
        # Format response
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'image_url': image_url,
            'detections': detection_result['detections'],
            'count': len(detection_result['detections']),
            'inference_time': detection_result['inference_time'],
            'saved': should_save,
            'firebase_doc_id': firebase_doc_id
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
    finally:
        # Clean up temporary file
        if filepath and os.path.exists(filepath):
            os.remove(filepath)

@api_bp.route('/detect-live', methods=['POST'])
def detect_live():
    """
    Endpoint 2: Live Detection (Camera Stream)
    
    Request: JSON
    {
        "image": "base64_encoded_image_string",
        "save": false
    }
    
    Response: Detailed JSON with detection results
    """
    
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No image data provided'
            }), 400
        
        base64_image = data['image']
        should_save = data.get('save', False)
        
        # Preprocess base64 image
        image = ImageProcessor.preprocess_base64(base64_image)
        
        # Get detector instance
        detector = get_detector()
        
        # Run detection
        detection_result = detector.detect(image, img_size=640)
        
        image_url = None
        firebase_doc_id = None
        
        if should_save:
            # Decode base64 for upload
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            image_bytes = base64.b64decode(base64_image)
            
            # Upload to Cloudinary
            cloudinary_result = CloudinaryService.upload_image(image_bytes)
            
            if cloudinary_result['success']:
                image_url = cloudinary_result['url']
                
                # Save to Firebase
                firebase_data = {
                    'image_url': image_url,
                    'detections': detection_result['detections'],
                    'inference_time': detection_result['inference_time'],
                    'source': 'live_camera'
                }
                
                firebase_result = FirebaseService.save_detection(firebase_data)
                
                if firebase_result['success']:
                    firebase_doc_id = firebase_result['doc_id']
        
        # Format response
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'image_url': image_url,
            'detections': detection_result['detections'],
            'count': len(detection_result['detections']),
            'inference_time': detection_result['inference_time'],
            'saved': should_save,
            'firebase_doc_id': firebase_doc_id
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/history', methods=['GET'])
def get_history():
    """
    Get detection history from Firebase
    
    Query params:
    - limit: int (default=50)
    
    Response: List of past detections
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        result = FirebaseService.get_detections(limit=limit)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'detections': result['detections'],
                'count': len(result['detections'])
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500