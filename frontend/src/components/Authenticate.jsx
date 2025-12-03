import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { Camera, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';

function Authenticate() {
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [result, setResult] = useState(null);
  const webcamRef = useRef(null);
  const navigate = useNavigate();

  const authenticate = async () => {
    if (!cameraReady) {
      setStatus({ type: 'error', message: 'Camera not ready' });
      return;
    }

    setLoading(true);
    setResult(null);
    setStatus({ type: 'info', message: 'Capturing image...' });

    try {
      const imageSrc = webcamRef.current.getScreenshot();

      if (!imageSrc) {
        setStatus({ type: 'error', message: 'Failed to capture image' });
        setLoading(false);
        return;
      }

      setStatus({ type: 'info', message: 'Authenticating...' });

      const response = await axios.post('/api/authenticate', { image: imageSrc });

      if (response.data.success) {
        setResult({
          success: true,
          username: response.data.username,
          confidence: response.data.confidence,
        });
        setStatus({
          type: 'success',
          message: `Welcome back, ${response.data.username}! (Confidence: ${response.data.confidence}%)`,
        });
      } else {
        setResult({
          success: false,
          confidence: response.data.confidence,
        });
        setStatus({ type: 'error', message: response.data.message });
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Authentication failed';
      setResult({ success: false });
      setStatus({ type: 'error', message: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-card">
        <div className="page-header">
          <h2>Face Authentication</h2>
          <p>Look at the camera to authenticate</p>
        </div>

        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.type === 'success' && <CheckCircle size={20} />}
            {status.type === 'error' && <XCircle size={20} />}
            {status.type === 'info' && <Camera size={20} />}
            <span>{status.message}</span>
          </div>
        )}

        {result && (
          <div
            className="page-card"
            style={{
              background: result.success
                ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
                : 'linear-gradient(135deg, #ee0979 0%, #ff6a00 100%)',
              color: 'white',
              textAlign: 'center',
              marginBottom: '1.5rem',
            }}
          >
            <h3 style={{ marginBottom: '0.5rem', fontSize: '1.5rem' }}>
              {result.success ? '✓ Authentication Successful' : '✗ Authentication Failed'}
            </h3>
            {result.success && (
              <p style={{ fontSize: '1.2rem' }}>
                Welcome, <strong>{result.username}</strong>!
              </p>
            )}
            <p style={{ marginTop: '0.5rem', opacity: 0.9 }}>
              Confidence: {result.confidence}%
            </p>
          </div>
        )}

        <div className="form-group">
          <label>Face Capture</label>
          <div className="webcam-container" style={{ position: 'relative' }}>
            {/* Always render Webcam */}
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{ width: 640, height: 480, facingMode: 'user' }}
              onUserMedia={() => setCameraReady(true)}
              mirrored
            />
            {/* Overlay while camera is initializing */}
            {!cameraReady && (
              <div
                className="webcam-overlay"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  backgroundColor: 'rgba(0,0,0,0.4)',
                  color: 'white',
                }}
              >
                <Camera size={48} />
                <p>Initializing camera...</p>
              </div>
            )}
          </div>
        </div>

        <div className="button-group">
          <button className="btn btn-primary" onClick={authenticate} disabled={loading || !cameraReady}>
            {loading ? (
              <>
                <div className="loading-spinner" /> Authenticating...
              </>
            ) : (
              <>
                <Camera size={20} /> Authenticate
              </>
            )}
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/')} disabled={loading}>
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

export default Authenticate;