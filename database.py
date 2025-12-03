from pymongo import MongoClient
from datetime import datetime
import numpy as np
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.users = self.db.users
        self.login_attempts = self.db.login_attempts
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        self.users.create_index("username", unique=True)
        self.login_attempts.create_index([("timestamp", -1)])
    
    def add_user(self, username, full_name, email, face_encoding):
        """Add a new user with face encoding"""
        try:
            user_data = {
                'username': username,
                'full_name': full_name,
                'email': email,
                'face_encoding': face_encoding.tolist(),  # Convert numpy array to list
                'created_at': datetime.utcnow(),
                'last_login': None,
                'is_active': True
            }
            result = self.users.insert_one(user_data)
            return True, str(result.inserted_id)
        except Exception as e:
            return False, str(e)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return self.users.find_one({'username': username, 'is_active': True})
    
    def get_all_users(self):
        """Get all active users"""
        users = list(self.users.find({'is_active': True}, {
            '_id': 0,
            'username': 1,
            'full_name': 1,
            'email': 1,
            'created_at': 1,
            'last_login': 1
        }))
        return users
    
    def get_all_face_encodings(self):
        """Get all face encodings with usernames"""
        users = self.users.find({'is_active': True}, {
            'username': 1,
            'face_encoding': 1
        })
        
        encodings = {}
        for user in users:
            if 'face_encoding' in user:
                encodings[user['username']] = np.array(user['face_encoding'])
        
        return encodings
    
    def update_last_login(self, username):
        """Update user's last login time"""
        self.users.update_one(
            {'username': username},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    
    def delete_user(self, username):
        """Soft delete a user"""
        result = self.users.update_one(
            {'username': username},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0
    
    def log_login_attempt(self, username, success, confidence):
        """Log a login attempt"""
        attempt_data = {
            'username': username,
            'success': success,
            'confidence': confidence,
            'timestamp': datetime.utcnow()
        }
        self.login_attempts.insert_one(attempt_data)
    
    def get_login_history(self, limit=50):
        """Get recent login history"""
        history = list(self.login_attempts.find(
            {},
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))
        return history
    
    def get_user_stats(self):
        """Get user statistics"""
        total_users = self.users.count_documents({'is_active': True})
        total_attempts = self.login_attempts.count_documents({})
        successful_attempts = self.login_attempts.count_documents({'success': True})
        
        return {
            'total_users': total_users,
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': total_attempts - successful_attempts
        }