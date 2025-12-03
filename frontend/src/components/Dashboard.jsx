import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, Activity, CheckCircle, XCircle, UserPlus, Lock } from 'lucide-react';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({
    total_users: 0,
    total_attempts: 0,
    successful_attempts: 0,
    failed_attempts: 0
  });
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchStatistics();
  }, []);
  
  const fetchStatistics = async () => {
    try {
      const response = await axios.get('/api/statistics');
      if (response.data.success) {
        setStats(response.data.statistics);
      }
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="dashboard">
      <div className="welcome-card">
        <h1>Welcome to FaceAuth</h1>
        <p>Secure, password-free authentication using facial recognition</p>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon primary">
            <Users size={32} />
          </div>
          <div className="stat-content">
            <h3>{loading ? '...' : stats.total_users}</h3>
            <p>Registered Users</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon info">
            <Activity size={32} />
          </div>
          <div className="stat-content">
            <h3>{loading ? '...' : stats.total_attempts}</h3>
            <p>Total Attempts</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon success">
            <CheckCircle size={32} />
          </div>
          <div className="stat-content">
            <h3>{loading ? '...' : stats.successful_attempts}</h3>
            <p>Successful</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon danger">
            <XCircle size={32} />
          </div>
          <div className="stat-content">
            <h3>{loading ? '...' : stats.failed_attempts}</h3>
            <p>Failed</p>
          </div>
        </div>
      </div>
      
      <div className="action-cards">
        <Link to="/register" className="action-card">
          <div className="action-icon">
            <UserPlus size={40} />
          </div>
          <h3>Register User</h3>
          <p>Register a new user with facial recognition data</p>
        </Link>
        
        <Link to="/authenticate" className="action-card">
          <div className="action-icon">
            <Lock size={40} />
          </div>
          <h3>Authenticate</h3>
          <p>Authenticate using facial recognition</p>
        </Link>
        
        <Link to="/users" className="action-card">
          <div className="action-icon">
            <Users size={40} />
          </div>
          <h3>Manage Users</h3>
          <p>View and manage registered users</p>
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;