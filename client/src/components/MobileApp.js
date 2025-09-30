import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSocket } from '../contexts/SocketContext';
import { useAuth } from '../contexts/AuthContext';

const MobileContainer = styled.div`
  min-height: 100vh;
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
`;

const MobileHeader = styled.header`
  background: #2d2d2d;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const MobileTitle = styled.h1`
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
`;

const MobileMenuButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
`;

const MobileNav = styled.nav`
  background: #2d2d2d;
  border-top: 1px solid #444;
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
`;

const NavButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.active ? '#007bff' : '#ccc'};
  font-size: 12px;
  cursor: pointer;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 60px;
`;

const NavIcon = styled.span`
  font-size: 20px;
`;

const MobileContent = styled.div`
  flex: 1;
  padding: 16px;
  padding-bottom: 80px;
  overflow-y: auto;
`;

const MobileCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const MobileButton = styled.button`
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 8px;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const MobileInput = styled.input`
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const MobileGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
`;

const MobileApp = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [applications, setApplications] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user, logout } = useAuth();
  const { socket, connected } = useSocket();

  useEffect(() => {
    loadApplications();
    loadSessions();
  }, []);

  const loadApplications = async () => {
    try {
      const response = await fetch('/api/applications', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setApplications(data);
    } catch (error) {
      console.error('Error loading applications:', error);
    }
  };

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/sessions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setSessions(data);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const startApplication = async (appName) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/applications/${appName}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        alert('Application started successfully');
      }
    } catch (error) {
      console.error('Error starting application:', error);
      alert('Failed to start application');
    } finally {
      setLoading(false);
    }
  };

  const renderHome = () => (
    <MobileContent>
      <MobileCard>
        <h2>Welcome, {user?.username}</h2>
        <p>Connection: {connected ? 'Connected' : 'Disconnected'}</p>
      </MobileCard>

      <MobileCard>
        <h3>Quick Actions</h3>
        <MobileButton onClick={() => setActiveTab('apps')}>
          View Applications
        </MobileButton>
        <MobileButton onClick={() => setActiveTab('sessions')}>
          Join Session
        </MobileButton>
        <MobileButton onClick={() => window.location.href = '/live'}>
          Live Stream
        </MobileButton>
      </MobileCard>

      <MobileCard>
        <h3>Recent Activity</h3>
        <p>No recent activity</p>
      </MobileCard>
    </MobileContent>
  );

  const renderApplications = () => (
    <MobileContent>
      <MobileCard>
        <h3>Available Applications</h3>
        {applications.map((app) => (
          <MobileCard key={app.name}>
            <h4>{app.display_name}</h4>
            <p>{app.description}</p>
            <MobileButton 
              onClick={() => startApplication(app.name)}
              disabled={loading}
            >
              {loading ? 'Starting...' : 'Launch'}
            </MobileButton>
          </MobileCard>
        ))}
      </MobileCard>
    </MobileContent>
  );

  const renderSessions = () => (
    <MobileContent>
      <MobileCard>
        <h3>Active Sessions</h3>
        {sessions.length > 0 ? (
          sessions.map((session) => (
            <MobileCard key={session.id}>
              <h4>{session.name}</h4>
              <p>Participants: {session.participant_count}</p>
              <MobileButton onClick={() => joinSession(session.id)}>
                Join Session
              </MobileButton>
            </MobileCard>
          ))
        ) : (
          <p>No active sessions</p>
        )}
        <MobileButton onClick={createSession}>
          Create New Session
        </MobileButton>
      </MobileCard>
    </MobileContent>
  );

  const renderSettings = () => (
    <MobileContent>
      <MobileCard>
        <h3>Settings</h3>
        <MobileInput
          type="text"
          placeholder="Server URL"
          defaultValue="localhost:3000"
        />
        <MobileInput
          type="number"
          placeholder="Quality (1-100)"
          defaultValue="80"
        />
        <MobileButton>Save Settings</MobileButton>
      </MobileCard>

      <MobileCard>
        <h3>Account</h3>
        <p>Username: {user?.username}</p>
        <MobileButton onClick={logout} style={{ background: '#dc3545' }}>
          Logout
        </MobileButton>
      </MobileCard>
    </MobileContent>
  );

  const joinSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/sessions/${sessionId}/join`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        alert('Joined session successfully');
        loadSessions();
      }
    } catch (error) {
      console.error('Error joining session:', error);
      alert('Failed to join session');
    }
  };

  const createSession = async () => {
    const sessionName = prompt('Enter session name:');
    if (!sessionName) return;

    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: sessionName })
      });
      
      if (response.ok) {
        alert('Session created successfully');
        loadSessions();
      }
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session');
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'apps':
        return renderApplications();
      case 'sessions':
        return renderSessions();
      case 'settings':
        return renderSettings();
      default:
        return renderHome();
    }
  };

  return (
    <MobileContainer>
      <MobileHeader>
        <MobileTitle>Application Share</MobileTitle>
        <MobileMenuButton onClick={() => setActiveTab('settings')}>
          ⚙️
        </MobileMenuButton>
      </MobileHeader>

      {renderContent()}

      <MobileNav>
        <NavButton 
          active={activeTab === 'home'} 
          onClick={() => setActiveTab('home')}
        >
          <NavIcon>🏠</NavIcon>
          Home
        </NavButton>
        <NavButton 
          active={activeTab === 'apps'} 
          onClick={() => setActiveTab('apps')}
        >
          <NavIcon>📱</NavIcon>
          Apps
        </NavButton>
        <NavButton 
          active={activeTab === 'sessions'} 
          onClick={() => setActiveTab('sessions')}
        >
          <NavIcon>👥</NavIcon>
          Sessions
        </NavButton>
        <NavButton 
          active={activeTab === 'settings'} 
          onClick={() => setActiveTab('settings')}
        >
          <NavIcon>⚙️</NavIcon>
          Settings
        </NavButton>
      </MobileNav>
    </MobileContainer>
  );
};

export default MobileApp;
