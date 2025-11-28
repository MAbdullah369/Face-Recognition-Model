import cv2
import numpy as np
import pickle
import os
from PIL import Image, ImageTk

class FaceEngine:
    def __init__(self):
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Face database
        self.face_database = {}
        self.load_database()
    
    def load_database(self):
        """Load face database"""
        try:
            if os.path.exists('models/face_database.pkl'):
                with open('models/face_database.pkl', 'rb') as f:
                    self.face_database = pickle.load(f)
                print(f"✅ Loaded {len(self.face_database)} face encodings")
        except Exception as e:
            print(f"⚠️ Starting fresh: {e}")
            self.face_database = {}
    
    def save_database(self):
        """Save face database"""
        with open('models/face_database.pkl', 'wb') as f:
            pickle.dump(self.face_database, f)
    
    def detect_faces(self, image):
        """Detect faces in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces, gray
    
    def extract_face_features(self, face_roi):
      
        # Resize to standard size
        face_roi = cv2.resize(face_roi, (100, 100))
        
        
        hist = cv2.calcHist([face_roi], [0], None, [64], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        return hist
    
    def compare_features(self, features1, features2):
        """Compare two feature sets using correlation"""
        if len(features1) != len(features2):
            return 0.0
        
        # Use correlation coefficient as similarity measure
        correlation = np.corrcoef(features1, features2)[0, 1]
        return max(0.0, correlation)  # Return between 0 and 1
    
    def register_face(self, username, image):
        """Register a new face"""
        faces, gray = self.detect_faces(image)
        
        if len(faces) != 1:
            return False, "Please ensure exactly one face is visible"
        
        # Extract face region
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # Extract features
        features = self.extract_face_features(face_roi)
        
        # Store in database
        self.face_database[username] = features
        self.save_database()
        
        return True, f"Face registered successfully for {username}"
    
    def authenticate_face(self, image):
        """Authenticate face using feature matching"""
        if len(self.face_database) == 0:
            return False, "No faces registered yet", 0.0, None
        
        faces, gray = self.detect_faces(image)
        
        if len(faces) != 1:
            return False, "Please ensure exactly one face is visible", 0.0, None
        
        # Extract face region and features
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        input_features = self.extract_face_features(face_roi)
        
        # Compare with all registered faces
        best_match = None
        best_similarity = 0.0
        threshold = 0.6  # Similarity threshold
        
        for username, stored_features in self.face_database.items():
            similarity = self.compare_features(input_features, stored_features)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = username
        
        if best_match and best_similarity > threshold:
            return True, f"Authenticated as {best_match}", best_similarity * 100, best_match
        else:
            return False, "Authentication failed", best_similarity * 100, None
    
    def get_camera_frame(self, camera):
        """Get frame from camera with face detection"""
        ret, frame = camera.read()
        if ret:
            # Detect faces
            faces, gray = self.detect_faces(frame)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, 'Face Detected', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Convert to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb, len(faces)
        return None, 0
    
    def delete_face(self, username):
        """Delete face from database"""
        if username in self.face_database:
            del self.face_database[username]
            self.save_database()
            return True
        return False