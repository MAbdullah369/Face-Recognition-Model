import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { Camera, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    full_name: '',
    email: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const webcamRef = useRef(null);
  const navigate = useNavigate();
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  
  const captureAndRegister = async () => {
    if (!formData.username.trim()) {
      setStatus({ type: 'error', message: 'Username is required' });
      return;
    }
    
    if (!cameraReady) {
      setStatus({ type: 'error', message: 'Camera not ready' });
      return;
    }
    
    setLoading(true);
    setStatus({ type: 'info', message: 'Capturing image...' });
    
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      
      if (!imageSrc) {
        setStatus({ type: 'error', message: 'Failed to capture image' });
        setLoading(false);
        return;
      }
      
      setStatus({ type: 'info', message: 'Processing face data...' });
      
      const response = await axios.post('/api/register', {
        username: formData.username.trim(),
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        image: imageSrc
      });
      
      if (response.data.success) {
        setStatus({ type: 'success', message: response.data.message });
        setTimeout(() => {
          navigate('/users');
        }, 2000);
      } else {
        setStatus({ type: 'error', message: response.data.message });
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Registration failed';
      setStatus({ type: 'error', message: errorMsg });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="page-container">
      <div className="page-card">
        <div className="page-header">
          <h2>Register New User</h2>
          <p>Enter user details and capture facial data</p>
        </div>
        
        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.type === 'success' && <CheckCircle size={20} />}
            {status.type === 'error' && <AlertCircle size={20} />}
            {status.type === 'info' && <Camera size={20} />}
            <span>{status.message}</span>
          </div>
        )}
        
        <div className="form-group">
          <label>Username *</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Enter username"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label>Full Name</label>
          <input
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Enter full name"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter email"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label>Face Capture</label>
          <div className="webcam-container">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{ width: 640, height: 480, facingMode: "user" }}
                onUserMedia={() => setCameraReady(true)}
                mirrored
              />

              {!cameraReady && (
                <div className="webcam-overlay">
                  <Camera size={48} />
                  <p>Initializing camera...</p>
                </div>
              )}
            </div>

        </div>
        
        <div className="button-group">
          <button
            className="btn btn-primary"
            onClick={captureAndRegister}
            disabled={loading || !cameraReady}
          >
            {loading ? (
              <>
                <div className="loading-spinner" />
                Processing...
              </>
            ) : (
              <>
                <Camera size={20} />
                Capture & Register
              </>
            )}
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/')}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default Register;