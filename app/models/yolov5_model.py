"""
YOLOv5 Model Handler - Singleton Pattern
Load model once, reuse for all requests
"""

import torch
import numpy as np
from pathlib import Path
from flask import current_app
import time

class YOLOv5Detector:
    """Singleton class for YOLOv5 model"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern - only one instance"""
        if cls._instance is None:
            cls._instance = super(YOLOv5Detector, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize model (only once)"""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load YOLOv5 model from weights"""
        try:
            model_path = current_app.config['MODEL_PATH']
            
            print(f"🔄 Loading YOLOv5 model from: {model_path}")
            
            # Use Ultralytics YOLO instead of torch.hub
            from ultralytics import YOLO
            
            self._model = YOLO(model_path)
            
            # Set confidence threshold
            self._model.conf = current_app.config['CONFIDENCE_THRESHOLD']
            self._model.iou = current_app.config['IOU_THRESHOLD']
            
            # Force CPU
            self._model.cpu()
            
            print(f"✅ Model loaded successfully!")
            print(f"   - Confidence threshold: {self._model.conf}")
            print(f"   - IOU threshold: {self._model.iou}")
            print(f"   - Classes: {current_app.config['CLASS_NAMES']}")
            
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise
    
    def detect(self, image, img_size=640):
        """
        Run detection on image
        
        Args:
            image: PIL Image or numpy array
            img_size: Input image size for model
            
        Returns:
            dict: Detection results with format:
            {
                'detections': [...],
                'inference_time': '...',
                'image_shape': (h, w)
            }
        """
        try:
            start_time = time.time()
            
            # Run inference with Ultralytics YOLO
            results = self._model(image, imgsz=img_size)
            
            inference_time = time.time() - start_time
            
            # Parse results
            detections = self._parse_results(results)
            
            return {
                'detections': detections,
                'inference_time': f"{inference_time*1000:.1f}ms",
                'image_shape': image.shape[:2] if hasattr(image, 'shape') else None
            }
            
        except Exception as e:
            print(f"❌ Detection error: {str(e)}")
            raise
    
    def _parse_results(self, results):
        """
        Parse Ultralytics YOLO results to custom format
        
        Args:
            results: Ultralytics YOLO results object
            
        Returns:
            list: List of detections
        """
        detections = []
        class_names = current_app.config['CLASS_NAMES']
        
        # Get results for first image
        result = results[0]
        
        # Get boxes, confidences, and class IDs
        boxes = result.boxes.xyxy.cpu().numpy()  # [x_min, y_min, x_max, y_max]
        confs = result.boxes.conf.cpu().numpy()  # confidence scores
        class_ids = result.boxes.cls.cpu().numpy()  # class IDs
        
        for i in range(len(boxes)):
            x_min, y_min, x_max, y_max = boxes[i]
            conf = confs[i]
            cls_id = int(class_ids[i])
            
            # Get class name
            class_name = class_names[cls_id] if cls_id < len(class_names) else f"class_{cls_id}"
            
            # Calculate width and height
            width = x_max - x_min
            height = y_max - y_min
            
            detection = {
                'class': class_name,
                'confidence': round(float(conf), 3),
                'bbox': {
                    'x_min': int(x_min),
                    'y_min': int(y_min),
                    'x_max': int(x_max),
                    'y_max': int(y_max),
                    'width': int(width),
                    'height': int(height)
                }
            }
            
            detections.append(detection)
        
        return detections
    
    @property
    def is_loaded(self):
        """Check if model is loaded"""
        return self._model is not None


# Global instance
detector = None

def get_detector():
    """Get or create detector instance"""
    global detector
    if detector is None:
        detector = YOLOv5Detector()
    return detector