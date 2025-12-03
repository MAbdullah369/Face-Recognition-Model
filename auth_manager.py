from database import Database
from face_engine import FaceEngine

class AuthManager:
    def __init__(self):
        self.db = Database()
        self.face_engine = FaceEngine()
    
    def register_user(self, username, full_name, email, base64_image):
        """Register a new user with face data"""
        # Validate input
        if not username or not username.strip():
            return {
                'success': False,
                'message': 'Username cannot be empty'
            }
        
        username = username.strip()
        
        # Check if user already exists
        if self.db.get_user_by_username(username):
            return {
                'success': False,
                'message': 'Username already exists'
            }
        
        # Process face image
        success, message, encoding = self.face_engine.process_image_for_registration(base64_image)
        
        if not success:
            return {
                'success': False,
                'message': message
            }
        
        # Add user to database
        success, result = self.db.add_user(username, full_name, email, encoding)
        
        if success:
            return {
                'success': True,
                'message': f'User {username} registered successfully',
                'user_id': result
            }
        else:
            return {
                'success': False,
                'message': f'Failed to register user: {result}'
            }
    
    def authenticate_user(self, base64_image):
        """Authenticate user using face recognition"""
        # Get all stored face encodings
        stored_encodings = self.db.get_all_face_encodings()
        
        if not stored_encodings:
            return {
                'success': False,
                'message': 'No users registered yet',
                'confidence': 0.0,
                'username': None
            }
        
        # Process image and compare
        success, message, confidence, username = self.face_engine.process_image_for_authentication(
            base64_image, 
            stored_encodings
        )
        
        # Log attempt
        self.db.log_login_attempt(
            username if username else 'Unknown',
            success,
            confidence
        )
        
        # Update last login if successful
        if success and username:
            self.db.update_last_login(username)
        
        return {
            'success': success,
            'message': message,
            'confidence': round(confidence, 2),
            'username': username
        }
    
    def get_all_users(self):
        """Get all registered users"""
        users = self.db.get_all_users()
        return {
            'success': True,
            'users': users,
            'count': len(users)
        }
    
    def delete_user(self, username):
        """Delete a user"""
        success = self.db.delete_user(username)
        
        if success:
            return {
                'success': True,
                'message': f'User {username} deleted successfully'
            }
        else:
            return {
                'success': False,
                'message': f'User {username} not found'
            }
    
    def get_login_history(self, limit=50):
        """Get login history"""
        history = self.db.get_login_history(limit)
        return {
            'success': True,
            'history': history,
            'count': len(history)
        }
    
    def get_statistics(self):
        """Get system statistics"""
        stats = self.db.get_user_stats()
        return {
            'success': True,
            'statistics': stats
        }