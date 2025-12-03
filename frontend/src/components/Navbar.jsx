import { Link, useLocation } from 'react-router-dom';
import { Home, UserPlus, Lock, Users } from 'lucide-react';

function Navbar() {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-brand">
          <Lock size={32} />
          <span>FaceAuth</span>
        </div>
        <div className="navbar-links">
          <Link 
            to="/" 
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            <Home size={20} />
            Dashboard
          </Link>
          <Link 
            to="/register" 
            className={`nav-link ${isActive('/register') ? 'active' : ''}`}
          >
            <UserPlus size={20} />
            Register
          </Link>
          <Link 
            to="/authenticate" 
            className={`nav-link ${isActive('/authenticate') ? 'active' : ''}`}
          >
            <Lock size={20} />
            Authenticate
          </Link>
          <Link 
            to="/users" 
            className={`nav-link ${isActive('/users') ? 'active' : ''}`}
          >
            <Users size={20} />
            Users
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;