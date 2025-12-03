from flask import Flask, request, jsonify
from flask_cors import CORS
from auth_manager import AuthManager
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize Auth Manager
auth_manager = AuthManager()

# Create upload folder if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Face Recognition API is running'
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'username' not in data or 'image' not in data:
            return jsonify({
                'success': False,
                'message': 'Username and image are required'
            }), 400
        
        username = data.get('username')
        full_name = data.get('full_name', '')
        email = data.get('email', '')
        image = data.get('image')
        
        # Register user
        result = auth_manager.register_user(username, full_name, email, image)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """Authenticate a user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'message': 'Image is required'
            }), 400
        
        image = data.get('image')
        
        # Authenticate user
        result = auth_manager.authenticate_user(image)
        
        status_code = 200 if result['success'] else 401
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all registered users"""
    try:
        result = auth_manager.get_all_users()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/users/<username>', methods=['DELETE'])
def delete_user(username):
    """Delete a user"""
    try:
        result = auth_manager.delete_user(username)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get login history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        result = auth_manager.get_login_history(limit)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        result = auth_manager.get_statistics()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Face Recognition API...")
    print(f"📡 Server running on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)