"""
Firebase Firestore Service
Save detection metadata to Firebase
"""

import firebase_admin
from firebase_admin import credentials, firestore
from flask import current_app
from datetime import datetime

class FirebaseService:
    """Service for saving detection results to Firebase"""
    
    _db = None
    _initialized = False
    
    @classmethod
    def init_firebase(cls):
        """Initialize Firebase Admin SDK"""
        if not cls._initialized:
            try:
                cred_path = current_app.config['FIREBASE_CREDENTIALS_PATH']
                
                # Initialize Firebase
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': current_app.config['FIREBASE_DATABASE_URL']
                })
                
                cls._db = firestore.client()
                cls._initialized = True
                
                print("✅ Firebase initialized successfully!")
                
            except Exception as e:
                print(f"❌ Firebase initialization error: {str(e)}")
                raise
    
    @classmethod
    def save_detection(cls, detection_data):
        """
        Save detection result to Firestore
        
        Args:
            detection_data: dict with detection info
            
        Returns:
            dict: Save result with document ID
        """
        try:
            if not cls._initialized:
                cls.init_firebase()
            
            # Add timestamp
            detection_data['timestamp'] = firestore.SERVER_TIMESTAMP
            detection_data['created_at'] = datetime.utcnow().isoformat()
            
            # Save to Firestore
            doc_ref = cls._db.collection('detections').add(detection_data)
            
            return {
                'success': True,
                'doc_id': doc_ref[1].id
            }
            
        except Exception as e:
            print(f"❌ Firebase save error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def get_detections(cls, limit=50):
        """
        Get recent detections from Firestore
        
        Args:
            limit: Maximum number of detections to retrieve
            
        Returns:
            list: List of detection documents
        """
        try:
            if not cls._initialized:
                cls.init_firebase()
            
            docs = cls._db.collection('detections')\
                         .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                         .limit(limit)\
                         .stream()
            
            detections = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                detections.append(data)
            
            return {
                'success': True,
                'detections': detections
            }
            
        except Exception as e:
            print(f"❌ Firebase get error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }