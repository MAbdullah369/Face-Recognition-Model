import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'face_recognition_db')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Face Recognition Configuration
    FACE_DETECTION_CONFIDENCE = 0.6
    FACE_MATCH_THRESHOLD = 0.6
    IMAGE_SIZE = (100, 100)
    
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True