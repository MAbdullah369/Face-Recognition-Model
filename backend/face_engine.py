import cv2
import numpy as np
from config import Config
import base64

class FaceEngine:
    def __init__(self):
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_faces(self, image):
        """Detect faces in an image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces, gray
    
    def validate_face(self, image, face_coords):
        """Validate that the detected face has eyes (liveness check)"""
        x, y, w, h = face_coords
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y:y+h, x:x+w]
        
        eyes = self.eye_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(20, 20)
        )
        
        # Check if at least 2 eyes are detected
        return len(eyes) >= 2
    
    def extract_face_encoding(self, image, face_coords):
        """Extract face encoding from detected face"""
        x, y, w, h = face_coords
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Extract face ROI
        face_roi = gray[y:y+h, x:x+w]
        
        # Resize to standard size
        face_roi = cv2.resize(face_roi, Config.IMAGE_SIZE)
        
        # Apply histogram equalization for better features
        face_roi = cv2.equalizeHist(face_roi)
        
        # Extract multiple features
        features = []
        
        # 1. Histogram features
        hist = cv2.calcHist([face_roi], [0], None, [64], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        features.extend(hist)
        
        # 2. LBP-like features (simplified)
        lbp_features = self._extract_lbp_features(face_roi)
        features.extend(lbp_features)
        
        # 3. HOG-like features (simplified)
        hog_features = self._extract_gradient_features(face_roi)
        features.extend(hog_features)
        
        return np.array(features)
    
    def _extract_lbp_features(self, image):
        """Extract Local Binary Pattern-like features"""
        # Divide image into grid
        h, w = image.shape
        cell_h, cell_w = h // 4, w // 4
        features = []
        
        for i in range(4):
            for j in range(4):
                cell = image[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                hist = cv2.calcHist([cell], [0], None, [16], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                features.extend(hist)
        
        return features
    
    def _extract_gradient_features(self, image):
        """Extract gradient-based features"""
        # Calculate gradients
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate magnitude and angle
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Create histogram of magnitudes
        hist, _ = np.histogram(magnitude, bins=32, range=(0, 255))
        hist = hist / (hist.sum() + 1e-6)
        
        return hist.tolist()
    
    def compare_faces(self, encoding1, encoding2):
        """Compare two face encodings and return similarity score"""
        # Normalize encodings
        norm1 = encoding1 / (np.linalg.norm(encoding1) + 1e-6)
        norm2 = encoding2 / (np.linalg.norm(encoding2) + 1e-6)
        
        # Calculate multiple similarity metrics
        
        # 1. Cosine similarity
        cosine_sim = np.dot(norm1, norm2)
        
        # 2. Correlation coefficient
        correlation = np.corrcoef(encoding1, encoding2)[0, 1]
        
        # 3. Euclidean distance (inverted and normalized)
        euclidean_dist = np.linalg.norm(encoding1 - encoding2)
        max_dist = np.sqrt(len(encoding1))
        euclidean_sim = 1 - (euclidean_dist / max_dist)
        
        # Combine metrics (weighted average)
        similarity = (0.4 * cosine_sim + 0.3 * correlation + 0.3 * euclidean_sim)
        
        # Ensure similarity is between 0 and 1
        similarity = max(0.0, min(1.0, similarity))
        
        return similarity
    
    def decode_image(self, base64_string):
        """Decode base64 image string to numpy array"""
        try:
            # Remove header if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            img_data = base64.b64decode(base64_string)
            np_arr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            return image
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None
    
    def process_image_for_registration(self, base64_image):
        """Process image for user registration"""
        # Decode image
        image = self.decode_image(base64_image)
        if image is None:
            return False, "Failed to decode image", None
        
        # Detect faces
        faces, gray = self.detect_faces(image)
        
        if len(faces) == 0:
            return False, "No face detected. Please ensure your face is visible.", None
        
        if len(faces) > 1:
            return False, "Multiple faces detected. Please ensure only one person is in frame.", None
        
        # Validate face (check for eyes)
        if not self.validate_face(image, faces[0]):
            return False, "Face validation failed. Please face the camera directly.", None
        
        # Extract face encoding
        encoding = self.extract_face_encoding(image, faces[0])
        
        return True, "Face processed successfully", encoding
    
    def process_image_for_authentication(self, base64_image, stored_encodings):
        """Process image for authentication"""
        # Decode image
        image = self.decode_image(base64_image)
        if image is None:
            return False, "Failed to decode image", 0.0, None
        
        # Detect faces
        faces, gray = self.detect_faces(image)
        
        if len(faces) == 0:
            return False, "No face detected", 0.0, None
        
        if len(faces) > 1:
            return False, "Multiple faces detected", 0.0, None
        
        # Extract face encoding
        input_encoding = self.extract_face_encoding(image, faces[0])
        
        # Compare with all stored encodings
        best_match = None
        best_similarity = 0.0
        
        for username, stored_encoding in stored_encodings.items():
            similarity = self.compare_faces(input_encoding, stored_encoding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = username
        
        # Check if best match exceeds threshold
        if best_match and best_similarity >= Config.FACE_MATCH_THRESHOLD:
            return True, f"Authenticated as {best_match}", best_similarity * 100, best_match
        else:
            return False, "Face not recognized", best_similarity * 100, None