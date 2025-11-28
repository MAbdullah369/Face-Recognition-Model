import cv2
from database import DatabaseManager
from face_engine import FaceEngine  

class AuthenticationSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.face_engine = FaceEngine()  
        self.camera = None
    
    def initialize_camera(self):
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            # Set camera resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return self.camera.isOpened()
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def release_camera(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            cv2.destroyAllWindows()
    
    def register_user(self, username, full_name="", email=""):
        """Register a new user"""
        # Validate input
        if not username.strip():
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        # Check if user already exists
        if self.db.user_exists(username):
            return False, "Username already exists"
        
        # Add to database
        if not self.db.add_user(username, full_name, email):
            return False, "Failed to add user to database"
        
        return True, f"User {username} registered successfully"
    
    def capture_and_register_face(self, username):
        """Capture face and register it"""
        if not self.camera:
            return False, "Camera not initialized"
        
        # Capture frame
        ret, frame = self.camera.read()
        if not ret:
            return False, "Failed to capture image"
        
        # Register face
        success, message = self.face_engine.register_face(username, frame)
        return success, message
    
    def authenticate_user(self):
        """Authenticate user using face recognition"""
        if not self.camera:
            return False, "Camera not initialized", 0.0, None
        
        # Capture frame
        ret, frame = self.camera.read()
        if not ret:
            return False, "Failed to capture image", 0.0, None
        
        # Authenticate face
        success, message, confidence, username = self.face_engine.authenticate_face(frame)
        
        # Log attempt
        self.db.log_login_attempt(username if username else "Unknown", success, confidence)
        
        return success, message, confidence, username
    
    def get_camera_frame(self):
        """Get current camera frame with face detection"""
        if not self.camera:
            return None, 0
        return self.face_engine.get_camera_frame(self.camera)
    
    def get_users(self):
        """Get all registered users"""
        return self.db.get_all_users()
    
    def delete_user(self, username):
        """Delete a user"""
        success = self.db.delete_user(username)
        if success:
            self.face_engine.delete_face(username)
            return True, f"User {username} deleted successfully"
        return False, f"User {username} not found"
    
    def get_login_history(self):
        """Get login history"""
        return self.db.get_login_history()