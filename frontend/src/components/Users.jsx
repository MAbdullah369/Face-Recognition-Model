import { useState, useEffect } from 'react';
import { Search, Trash2, RefreshCw, UserX } from 'lucide-react';
import axios from 'axios';

function Users() {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredUsers(users);
    } else {
      const filtered = users.filter(user =>
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredUsers(filtered);
    }
  }, [searchTerm, users]);
  
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/users');
      if (response.data.success) {
        setUsers(response.data.users);
        setFilteredUsers(response.data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const deleteUser = async (username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"?`)) {
      return;
    }
    
    try {
      const response = await axios.delete(`/api/users/${username}`);
      if (response.data.success) {
        alert(response.data.message);
        fetchUsers();
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert('Error deleting user');
    }
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };
  
  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
  
  return (
    <div>
      <div className="page-card">
        <div className="users-header">
          <h2>Registered Users ({filteredUsers.length})</h2>
          <div className="search-bar">
            <div style={{ position: 'relative', flex: 1 }}>
              <Search 
                size={20} 
                style={{ 
                  position: 'absolute', 
                  left: '12px', 
                  top: '50%', 
                  transform: 'translateY(-50%)',
                  color: '#999'
                }} 
              />
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ paddingLeft: '40px' }}
              />
            </div>
            <button className="btn btn-secondary" onClick={fetchUsers}>
              <RefreshCw size={20} />
              Refresh
            </button>
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="page-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="loading-spinner" style={{ margin: '0 auto 1rem' }} />
          <p>Loading users...</p>
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="page-card empty-state">
          <UserX size={64} style={{ margin: '0 auto', opacity: 0.3 }} />
          <h3>No Users Found</h3>
          <p>
            {searchTerm 
              ? 'No users match your search criteria' 
              : 'No users have been registered yet'}
          </p>
        </div>
      ) : (
        <div className="users-grid">
          {filteredUsers.map((user) => (
            <div key={user.username} className="user-card">
              <div className="user-avatar">
                {getInitials(user.full_name || user.username)}
              </div>
              <div className="user-info">
                <h3>{user.full_name || 'No name provided'}</h3>
                <div className="username">@{user.username}</div>
                <div className="email">{user.email || 'No email provided'}</div>
              </div>
              <div className="user-meta">
                <div>
                  <strong>Registered:</strong> {formatDate(user.created_at)}
                </div>
                <div>
                  <strong>Last Login:</strong> {formatDate(user.last_login)}
                </div>
              </div>
              <div className="user-actions">
                <button
                  className="btn btn-danger"
                  onClick={() => deleteUser(user.username)}
                  style={{ width: '100%' }}
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Users;