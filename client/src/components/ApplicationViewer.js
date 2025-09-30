import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useSocket } from '../contexts/SocketContext';
import axios from 'axios';

const ViewerContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
`;

const Header = styled.header`
  background: #2d2d2d;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #444;
`;

const AppTitle = styled.h1`
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
`;

const ControlButtons = styled.div`
  display: flex;
  gap: 8px;
`;

const ControlButton = styled.button`
  padding: 8px 16px;
  background: ${props => props.variant === 'danger' ? '#dc3545' : '#007bff'};
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.variant === 'danger' ? '#c82333' : '#0056b3'};
  }
`;

const ApplicationArea = styled.div`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #1a1a1a;
  position: relative;
  overflow: hidden;
`;

const ApplicationWindow = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  position: relative;
  min-width: 800px;
  min-height: 600px;
  max-width: 95vw;
  max-height: 95vh;
`;

const ScreenshotImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: contain;
  cursor: crosshair;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 18px;
`;

const ErrorMessage = styled.div`
  background: #dc3545;
  color: white;
  padding: 12px 20px;
  text-align: center;
  font-weight: 500;
`;

const StatusBar = styled.div`
  background: #2d2d2d;
  padding: 8px 20px;
  color: #ccc;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ConnectionStatus = styled.span`
  color: ${props => props.connected ? '#28a745' : '#dc3545'};
  font-weight: 600;
`;

const ApplicationViewer = () => {
  const { appId } = useParams();
  const navigate = useNavigate();
  const { socket, connected, joinApplication, sendMouseEvent, sendKeyboardEvent } = useSocket();
  const [screenshot, setScreenshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [appInfo, setAppInfo] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const windowRef = useRef(null);
  const screenshotIntervalRef = useRef(null);

  useEffect(() => {
    if (appId) {
      loadApplicationInfo();
      joinApplication(appId);
    }

    return () => {
      if (screenshotIntervalRef.current) {
        clearInterval(screenshotIntervalRef.current);
      }
    };
  }, [appId]);

  useEffect(() => {
    if (socket) {
      socket.on('screenshot_update', (data) => {
        setScreenshot(data.screenshot);
      });

      socket.on('app_update', (data) => {
        if (data.update_type === 'stopped') {
          setError('Application has been stopped');
        }
      });

      socket.on('error', (data) => {
        setError(data.message);
      });
    }

    return () => {
      if (socket) {
        socket.off('screenshot_update');
        socket.off('app_update');
        socket.off('error');
      }
    };
  }, [socket]);

  const loadApplicationInfo = async () => {
    try {
      const response = await axios.get(`/api/applications/${appId}/status`);
      setAppInfo(response.data);
      setLoading(false);
    } catch (error) {
      setError('Failed to load application information');
      setLoading(false);
    }
  };

  const startScreenshotUpdates = () => {
    if (screenshotIntervalRef.current) {
      clearInterval(screenshotIntervalRef.current);
    }

    screenshotIntervalRef.current = setInterval(async () => {
      try {
        const response = await axios.get(`/api/applications/${appId}/screenshot`);
        if (response.data.screenshot) {
          setScreenshot(response.data.screenshot);
        }
      } catch (error) {
        console.error('Error getting screenshot:', error);
      }
    }, 1000); // Update every second
  };

  useEffect(() => {
    if (appInfo && appInfo.status === 'running') {
      startScreenshotUpdates();
    }

    return () => {
      if (screenshotIntervalRef.current) {
        clearInterval(screenshotIntervalRef.current);
      }
    };
  }, [appInfo]);

  const handleMouseClick = (event) => {
    if (!screenshot || !windowRef.current) return;

    const rect = windowRef.current.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (800 / rect.width));
    const y = Math.round((event.clientY - rect.top) * (600 / rect.height));

    sendMouseEvent('click', x, y, 1);
  };

  const handleMouseMove = (event) => {
    if (!screenshot || !windowRef.current) return;

    const rect = windowRef.current.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (800 / rect.width));
    const y = Math.round((event.clientY - rect.top) * (600 / rect.height));

    sendMouseEvent('mousemove', x, y, 1);
  };

  const handleKeyPress = (event) => {
    event.preventDefault();
    
    // Map common keys
    const keyMap = {
      'Enter': 'Return',
      'Escape': 'Escape',
      'Backspace': 'BackSpace',
      'Tab': 'Tab',
      ' ': 'space',
      'ArrowUp': 'Up',
      'ArrowDown': 'Down',
      'ArrowLeft': 'Left',
      'ArrowRight': 'Right'
    };

    const key = keyMap[event.key] || event.key;
    const modifiers = [];

    if (event.ctrlKey) modifiers.push('ctrl');
    if (event.altKey) modifiers.push('alt');
    if (event.shiftKey) modifiers.push('shift');
    if (event.metaKey) modifiers.push('meta');

    sendKeyboardEvent(key, modifiers);
  };

  const stopApplication = async () => {
    try {
      await axios.post(`/api/applications/${appId}/stop`);
      navigate('/dashboard');
    } catch (error) {
      console.error('Error stopping application:', error);
      alert('Failed to stop application');
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (loading) {
    return (
      <ViewerContainer>
        <LoadingOverlay>
          <div className="spinner"></div>
          <span style={{ marginLeft: '12px' }}>Loading application...</span>
        </LoadingOverlay>
      </ViewerContainer>
    );
  }

  if (error) {
    return (
      <ViewerContainer>
        <Header>
          <AppTitle>Application Error</AppTitle>
          <ControlButtons>
            <ControlButton onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </ControlButton>
          </ControlButtons>
        </Header>
        <ErrorMessage>{error}</ErrorMessage>
      </ViewerContainer>
    );
  }

  return (
    <ViewerContainer>
      <Header>
        <AppTitle>
          {appInfo?.name || 'Application'} 
          {appInfo?.status && ` (${appInfo.status})`}
        </AppTitle>
        <ControlButtons>
          <ControlButton onClick={toggleFullscreen}>
            {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </ControlButton>
          <ControlButton onClick={stopApplication} variant="danger">
            Stop Application
          </ControlButton>
          <ControlButton onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </ControlButton>
        </ControlButtons>
      </Header>

      <ApplicationArea>
        <ApplicationWindow
          ref={windowRef}
          onClick={handleMouseClick}
          onMouseMove={handleMouseMove}
          onKeyDown={handleKeyPress}
          tabIndex={0}
          style={{
            width: isFullscreen ? '100vw' : '800px',
            height: isFullscreen ? '100vh' : '600px',
            maxWidth: isFullscreen ? '100vw' : '95vw',
            maxHeight: isFullscreen ? '100vh' : '95vh'
          }}
        >
          {screenshot ? (
            <ScreenshotImage
              src={screenshot}
              alt="Application Screenshot"
              onLoad={() => setLoading(false)}
            />
          ) : (
            <LoadingOverlay>
              <div className="spinner"></div>
              <span style={{ marginLeft: '12px' }}>Waiting for application...</span>
            </LoadingOverlay>
          )}
        </ApplicationWindow>
      </ApplicationArea>

      <StatusBar>
        <div>
          Connection: <ConnectionStatus connected={connected}>
            {connected ? 'Connected' : 'Disconnected'}
          </ConnectionStatus>
        </div>
        <div>
          Application ID: {appId}
        </div>
      </StatusBar>
    </ViewerContainer>
  );
};

export default ApplicationViewer;
