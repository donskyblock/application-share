import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const DashboardContainer = styled.div`
  min-height: 100vh;
  padding: 20px;
`;

const Header = styled.header`
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px 30px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  color: #2c3e50;
  font-size: 32px;
  font-weight: 700;
  margin: 0;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const Username = styled.span`
  color: #2c3e50;
  font-weight: 600;
`;

const LogoutButton = styled.button`
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &:hover {
    background: #c82333;
    transform: translateY(-1px);
  }
`;

const ApplicationsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const ApplicationCard = styled(motion.div)`
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
`;

const AppIcon = styled.div`
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-bottom: 16px;
`;

const AppName = styled.h3`
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 8px;
`;

const AppDescription = styled.p`
  color: #6c757d;
  font-size: 14px;
  margin-bottom: 16px;
`;

const LaunchButton = styled.button`
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #0056b3;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const RunningAppsSection = styled.div`
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
`;

const SectionTitle = styled.h2`
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
`;

const RunningAppCard = styled.div`
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const AppInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AppStatus = styled.span`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background: #28a745;
  color: white;
`;

const ActionButton = styled.button`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
`;

const ViewButton = styled(ActionButton)`
  background: #007bff;
  color: white;
  margin-right: 8px;
  
  &:hover {
    background: #0056b3;
  }
`;

const StopButton = styled(ActionButton)`
  background: #dc3545;
  color: white;
  
  &:hover {
    background: #c82333;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
`;

const Dashboard = () => {
  const [applications, setApplications] = useState([]);
  const [runningApps, setRunningApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startingApp, setStartingApp] = useState(null);
  const [vncInfo, setVncInfo] = useState(null);
  const [rdpInfo, setRdpInfo] = useState(null);
  const [streamInfo, setStreamInfo] = useState(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadApplications();
    loadRunningApps();
    loadVncInfo();
    loadRdpInfo();
    loadStreamInfo();
  }, []);

  const loadApplications = async () => {
    try {
      const response = await axios.get('/api/applications');
      setApplications(response.data);
    } catch (error) {
      console.error('Error loading applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRunningApps = async () => {
    try {
      const response = await axios.get('/api/applications/running');
      setRunningApps(response.data);
    } catch (error) {
      console.error('Error loading running apps:', error);
    }
  };

  const loadVncInfo = async () => {
    try {
      const response = await axios.get('/api/vnc/info');
      setVncInfo(response.data);
    } catch (error) {
      console.error('Error loading VNC info:', error);
    }
  };

  const loadRdpInfo = async () => {
    try {
      const response = await axios.get('/api/rdp/info');
      setRdpInfo(response.data);
    } catch (error) {
      console.error('Error loading RDP info:', error);
    }
  };

  const loadStreamInfo = async () => {
    try {
      const response = await axios.get('/api/stream/info');
      setStreamInfo(response.data);
    } catch (error) {
      console.error('Error loading stream info:', error);
    }
  };

  const startApplication = async (appName) => {
    setStartingApp(appName);
    try {
      const response = await axios.post(`/api/applications/${appName}/start`);
      const { app_id } = response.data;
      
      // Navigate to application viewer
      navigate(`/app/${app_id}`);
    } catch (error) {
      console.error('Error starting application:', error);
      alert('Failed to start application');
    } finally {
      setStartingApp(null);
    }
  };

  const stopApplication = async (appId) => {
    try {
      await axios.post(`/api/applications/${appId}/stop`);
      loadRunningApps(); // Refresh the list
    } catch (error) {
      console.error('Error stopping application:', error);
      alert('Failed to stop application');
    }
  };

  const viewApplication = (appId) => {
    navigate(`/app/${appId}`);
  };

  if (loading) {
    return (
      <LoadingSpinner>
        <div className="spinner"></div>
      </LoadingSpinner>
    );
  }

  return (
    <DashboardContainer>
      <Header>
        <Title>Application Share</Title>
        <UserInfo>
          <Username>Welcome, {user?.username}</Username>
          <LogoutButton onClick={logout}>Logout</LogoutButton>
        </UserInfo>
      </Header>

      <ApplicationsGrid>
        {applications.map((app) => (
          <ApplicationCard
            key={app.name}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <AppIcon>📱</AppIcon>
            <AppName>{app.display_name}</AppName>
            <AppDescription>{app.description}</AppDescription>
            <LaunchButton
              onClick={() => startApplication(app.name)}
              disabled={startingApp === app.name}
            >
              {startingApp === app.name ? (
                <>
                  <div className="spinner" style={{ marginRight: '8px' }}></div>
                  Starting...
                </>
              ) : (
                'Launch Application'
              )}
            </LaunchButton>
          </ApplicationCard>
        ))}
      </ApplicationsGrid>

      {/* Live Stream Section */}
      <RunningAppsSection>
        <SectionTitle>Live Stream & VNC</SectionTitle>
        <RunningAppCard>
          <AppInfo>
            <div>
              <strong>Live Stream</strong>
              <div style={{ fontSize: '12px', color: '#6c757d' }}>
                Real-time screen sharing
                {streamInfo && ` | ${streamInfo.clients} clients | ${streamInfo.frame_rate} FPS`}
              </div>
            </div>
            <AppStatus style={{ background: streamInfo?.streaming ? '#28a745' : '#dc3545' }}>
              {streamInfo?.streaming ? 'Live' : 'Offline'}
            </AppStatus>
          </AppInfo>
          <div>
            <ViewButton onClick={() => navigate('/live')}>
              View Live Stream
            </ViewButton>
          </div>
        </RunningAppCard>
        
        {vncInfo && (
          <RunningAppCard>
            <AppInfo>
              <div>
                <strong>VNC Server</strong>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>
                  Port {vncInfo.port} | Display {vncInfo.display}
                  {vncInfo.password_required && ' | Password Required'}
                </div>
              </div>
              <AppStatus style={{ background: vncInfo.running ? '#28a745' : '#dc3545' }}>
                {vncInfo.running ? 'Running' : 'Stopped'}
              </AppStatus>
            </AppInfo>
            <div>
              {vncInfo.running ? (
                <StopButton onClick={() => {
                  fetch('/api/vnc/stop', { method: 'POST' });
                  loadVncInfo();
                }}>
                  Stop VNC
                </StopButton>
              ) : (
                <ViewButton onClick={() => {
                  fetch('/api/vnc/start', { method: 'POST' });
                  loadVncInfo();
                }}>
                  Start VNC
                </ViewButton>
              )}
            </div>
          </RunningAppCard>
        )}
        
        {rdpInfo && (
          <RunningAppCard>
            <AppInfo>
              <div>
                <strong>RDP Server</strong>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>
                  Port {rdpInfo.port} | Display {rdpInfo.display}
                  {rdpInfo.password_required && ' | Password Required'}
                </div>
              </div>
              <AppStatus style={{ background: rdpInfo.running ? '#28a745' : '#dc3545' }}>
                {rdpInfo.running ? 'Running' : 'Stopped'}
              </AppStatus>
            </AppInfo>
            <div>
              {rdpInfo.running ? (
                <StopButton onClick={() => {
                  fetch('/api/rdp/stop', { method: 'POST' });
                  loadRdpInfo();
                }}>
                  Stop RDP
                </StopButton>
              ) : (
                <ViewButton onClick={() => {
                  fetch('/api/rdp/start', { method: 'POST' });
                  loadRdpInfo();
                }}>
                  Start RDP
                </ViewButton>
              )}
            </div>
          </RunningAppCard>
        )}
      </RunningAppsSection>

      {runningApps.length > 0 && (
        <RunningAppsSection>
          <SectionTitle>Running Applications</SectionTitle>
          {runningApps.map((app) => (
            <RunningAppCard key={app.id}>
              <AppInfo>
                <div>
                  <strong>{app.name}</strong>
                  <div style={{ fontSize: '12px', color: '#6c757d' }}>
                    Started: {new Date(app.started_at).toLocaleString()}
                  </div>
                </div>
                <AppStatus>{app.status}</AppStatus>
              </AppInfo>
              <div>
                <ViewButton onClick={() => viewApplication(app.id)}>
                  View
                </ViewButton>
                <StopButton onClick={() => stopApplication(app.id)}>
                  Stop
                </StopButton>
              </div>
            </RunningAppCard>
          ))}
        </RunningAppsSection>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;
