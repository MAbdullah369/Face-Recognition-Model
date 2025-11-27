import pickle
import os
import sqlite3
from typing import Dict, List, Tuple, Optional
import numpy as np

class DatabaseManager:
    def __init__(self, db_path: str = "face_auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for user management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, username: str) -> bool:
        """Add user to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_all_users(self) -> List[str]:
        """Get all registered usernames"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    
    def delete_user(self, username: str) -> bool:
        """Delete user from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except:
            return False

class FaceEncodingStorage:
    def __init__(self, storage_path: str = "models/face_database.pkl"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.face_encodings: Dict[str, np.ndarray] = self.load_encodings()
    
    def load_encodings(self) -> Dict[str, np.ndarray]:
        """Load face encodings from pickle file"""
        try:
            with open(self.storage_path, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return {}
    
    def save_encodings(self):
        """Save face encodings to pickle file"""
        with open(self.storage_path, 'wb') as f:
            pickle.dump(self.face_encodings, f)
    
    def add_encoding(self, username: str, encoding: np.ndarray):
        """Add face encoding for user"""
        self.face_encodings[username] = encoding
        self.save_encodings()
    
    def get_encoding(self, username: str) -> Optional[np.ndarray]:
        """Get face encoding for user"""
        return self.face_encodings.get(username)
    
    def get_all_encodings(self) -> Dict[str, np.ndarray]:
        """Get all face encodings"""
        return self.face_encodings
    
    def delete_encoding(self, username: str):
        """Delete face encoding for user"""
        if username in self.face_encodings:
            del self.face_encodings[username]
            self.save_encodings()