import face_recognition
import numpy as np
import cv2
from typing import Tuple, Optional, List, Dict
from database import DatabaseManager, FaceEncodingStorage

class FaceEngine:
    def __init__(self, tolerance: float = 0.5):
        self.tolerance = tolerance
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple]:
        """Detect faces in image and return face locations"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            return face_locations
        except Exception as e:
            print(f"Error in face detection: {e}")
            return []
    
    def encode_face(self, image: np.ndarray, face_location: Optional[Tuple] = None) -> Optional[np.ndarray]:
        """Encode face to 128-dimensional vector"""
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if face_location:
                face_encodings = face_recognition.face_encodings(rgb_image, [face_location])
            else:
                face_encodings = face_recognition.face_encodings(rgb_image)
            
            return face_encodings[0] if face_encodings else None
        except Exception as e:
            print(f"Error in face encoding: {e}")
            return None
    
    def compare_faces(self, known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> Tuple[bool, float]:
        """Compare two face encodings and return match result with confidence"""
        try:
            # Calculate Euclidean distance
            distance = np.linalg.norm(known_encoding - unknown_encoding)
            is_match = distance <= self.tolerance
            confidence = max(0.0, 1.0 - (distance / self.tolerance))
            return is_match, confidence
        except Exception as e:
            print(f"Error in face comparison: {e}")
            return False, 0.0

class AuthManager:
    def __init__(self):
        self.face_engine = FaceEngine(tolerance=0.5)
        self.db_manager = DatabaseManager()
        self.encoding_storage = FaceEncodingStorage()
    
    def register_user(self, username: str, image: np.ndarray) -> Dict:
        """Register a new user with face encoding"""
        try:
            # Validate input
            if not username or not username.strip():
                return {"success": False, "message": "Username cannot be empty"}
            
            username = username.strip()
            
            # Check if user already exists
            if self.db_manager.user_exists(username):
                return {"success": False, "message": "Username already exists"}
            
            # Detect and encode face
            face_locations = self.face_engine.detect_faces(image)
            if not face_locations:
                return {"success": False, "message": "No face detected. Please ensure your face is clearly visible"}
            
            if len(face_locations) > 1:
                return {"success": False, "message": "Multiple faces detected. Please ensure only one person is in frame"}
            
            face_encoding = self.face_engine.encode_face(image, face_locations[0])
            if face_encoding is None:
                return {"success": False, "message": "Could not process face. Please try again"}
            
            # Save user data
            if not self.db_manager.add_user(username):
                return {"success": False, "message": "Failed to add user to database"}
            
            self.encoding_storage.add_encoding(username, face_encoding)
            
            return {"success": True, "message": f"User '{username}' registered successfully!"}
            
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, image: np.ndarray) -> Dict:
        """Authenticate user using face recognition"""
        try:
            # Detect and encode face
            face_encoding = self.face_engine.encode_face(image)
            if face_encoding is None:
                return {"success": False, "message": "No face detected", "username": None}
            
            # Compare with all known encodings
            known_encodings = self.encoding_storage.get_all_encodings()
            best_match = None
            highest_confidence = 0.0
            
            for username, known_encoding in known_encodings.items():
                is_match, confidence = self.face_engine.compare_faces(known_encoding, face_encoding)
                if is_match and confidence > highest_confidence:
                    best_match = username
                    highest_confidence = confidence
            
            if best_match:
                return {
                    "success": True, 
                    "message": f"Authentication successful! Welcome {best_match}",
                    "username": best_match,
                    "confidence": highest_confidence
                }
            else:
                return {"success": False, "message": "Authentication failed. User not recognized", "username": None}
                
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}", "username": None}
    
    def get_registered_users(self) -> List[str]:
        """Get list of all registered users"""
        return self.db_manager.get_all_users()
    
    def delete_user(self, username: str) -> Dict:
        """Delete user from system"""
        try:
            success_db = self.db_manager.delete_user(username)
            self.encoding_storage.delete_encoding(username)
            
            if success_db:
                return {"success": True, "message": f"User '{username}' deleted successfully"}
            else:
                return {"success": False, "message": f"User '{username}' not found"}
                
        except Exception as e:
            return {"success": False, "message": f"Deletion failed: {str(e)}"}