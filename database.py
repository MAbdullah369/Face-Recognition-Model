import sqlite3
import pickle
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_path = "models/users.db"
        self.face_data_path = "models/face_data.pkl"
        self.init_database()
    
    def init_database(self):
        """Initialize database and storage directory"""
        os.makedirs("models", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize face data storage
        if not os.path.exists(self.face_data_path):
            with open(self.face_data_path, 'wb') as f:
                pickle.dump({}, f)
    
    def add_user(self, username, full_name="", email=""):
        """Add a new user to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, full_name, email) VALUES (?, ?, ?)",
                (username, full_name, email)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def user_exists(self, username):
        """Check if user exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND is_active = 1", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_all_users(self):
        """Get all active users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, full_name, email, created_at FROM users WHERE is_active = 1")
        users = cursor.fetchall()
        conn.close()
        return users
    
    def delete_user(self, username):
        """Soft delete a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def log_login_attempt(self, username, success, confidence=0.0):
        """Log login attempt for audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO login_attempts (username, success, confidence) VALUES (?, ?, ?)",
            (username, success, confidence)
        )
        
        if success:
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
                (username,)
            )
        
        conn.commit()
        conn.close()
    
    def get_login_history(self, limit=50):
        """Get recent login history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username, success, timestamp, confidence 
            FROM login_attempts 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        history = cursor.fetchall()
        conn.close()
        return history