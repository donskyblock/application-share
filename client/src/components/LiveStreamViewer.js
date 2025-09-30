import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useSocket } from '../contexts/SocketContext';

const StreamContainer = styled.div`
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

const Title = styled.h1`
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

const StreamArea = styled.div`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #1a1a1a;
  position: relative;
  overflow: hidden;
`;

const StreamCanvas = styled.canvas`
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  cursor: crosshair;
  max-width: 95vw;
  max-height: 95vh;
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

const QualityControl = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const QualitySlider = styled.input`
  width: 100px;
`;

const LiveStreamViewer = () => {
  const [streaming, setStreaming] = useState(false);
  const [connected, setConnected] = useState(false);
  const [frameRate, setFrameRate] = useState(0);
  const [quality, setQuality] = useState(80);
  const [error, setError] = useState(null);
  const [vncInfo, setVncInfo] = useState(null);
  
  const canvasRef = useRef(null);
  const websocketRef = useRef(null);
  const { socket } = useSocket();

  useEffect(() => {
    connectToLiveStream();
    loadVncInfo();
    
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  const connectToLiveStream = () => {
    try {
      const ws = new WebSocket('ws://localhost:8765');
      websocketRef.current = ws;
      
      ws.onopen = () => {
        console.log('Connected to live stream');
        setConnected(true);
        setStreaming(true);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'config') {
            setFrameRate(data.frame_rate);
            setQuality(data.quality);
          } else if (data.type === 'frame') {
            displayFrame(data.data);
          }
        } catch (err) {
          console.error('Error parsing stream data:', err);
        }
      };
      
      ws.onclose = () => {
        console.log('Disconnected from live stream');
        setConnected(false);
        setStreaming(false);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Failed to connect to live stream');
      };
      
    } catch (err) {
      console.error('Error connecting to live stream:', err);
      setError('Failed to connect to live stream');
    }
  };

  const displayFrame = (imageData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
    
    img.src = imageData;
  };

  const loadVncInfo = async () => {
    try {
      const response = await fetch('/api/vnc/info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const info = await response.json();
        setVncInfo(info);
      }
    } catch (err) {
      console.error('Error loading VNC info:', err);
    }
  };

  const handleMouseClick = (event) => {
    if (!websocketRef.current || !connected) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (canvas.width / rect.width));
    const y = Math.round((event.clientY - rect.top) * (canvas.height / rect.height));
    
    const message = {
      type: 'mouse',
      action: 'click',
      x: x,
      y: y,
      button: event.button + 1
    };
    
    websocketRef.current.send(JSON.stringify(message));
  };

  const handleMouseMove = (event) => {
    if (!websocketRef.current || !connected) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (canvas.width / rect.width));
    const y = Math.round((event.clientY - rect.top) * (canvas.height / rect.height));
    
    const message = {
      type: 'mouse',
      action: 'mousemove',
      x: x,
      y: y
    };
    
    websocketRef.current.send(JSON.stringify(message));
  };

  const handleKeyPress = (event) => {
    if (!websocketRef.current || !connected) return;
    
    event.preventDefault();
    
    const message = {
      type: 'keyboard',
      key: event.key,
      modifiers: []
    };
    
    if (event.ctrlKey) message.modifiers.push('ctrl');
    if (event.altKey) message.modifiers.push('alt');
    if (event.shiftKey) message.modifiers.push('shift');
    if (event.metaKey) message.modifiers.push('meta');
    
    websocketRef.current.send(JSON.stringify(message));
  };

  const handleWheel = (event) => {
    if (!websocketRef.current || !connected) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (canvas.width / rect.width));
    const y = Math.round((event.clientY - rect.top) * (canvas.height / rect.height));
    
    const message = {
      type: 'scroll',
      x: x,
      y: y,
      direction: event.deltaY > 0 ? 'down' : 'up'
    };
    
    websocketRef.current.send(JSON.stringify(message));
  };

  const startVnc = async () => {
    try {
      const response = await fetch('/api/vnc/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        loadVncInfo();
      }
    } catch (err) {
      console.error('Error starting VNC:', err);
    }
  };

  const stopVnc = async () => {
    try {
      const response = await fetch('/api/vnc/stop', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        loadVncInfo();
      }
    } catch (err) {
      console.error('Error stopping VNC:', err);
    }
  };

  if (error) {
    return (
      <StreamContainer>
        <Header>
          <Title>Live Stream Error</Title>
        </Header>
        <div style={{ padding: '20px', color: 'white', textAlign: 'center' }}>
          <h2>Error: {error}</h2>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </StreamContainer>
    );
  }

  return (
    <StreamContainer>
      <Header>
        <Title>Live Stream Viewer</Title>
        <ControlButtons>
          {vncInfo && (
            <>
              {vncInfo.running ? (
                <ControlButton onClick={stopVnc} variant="danger">
                  Stop VNC
                </ControlButton>
              ) : (
                <ControlButton onClick={startVnc}>
                  Start VNC
                </ControlButton>
              )}
            </>
          )}
          <ControlButton onClick={() => window.location.href = '/dashboard'}>
            Back to Dashboard
          </ControlButton>
        </ControlButtons>
      </Header>

      <StreamArea>
        <StreamCanvas
          ref={canvasRef}
          onClick={handleMouseClick}
          onMouseMove={handleMouseMove}
          onKeyDown={handleKeyPress}
          onWheel={handleWheel}
          tabIndex={0}
        />
        
        {!streaming && (
          <LoadingOverlay>
            <div className="spinner"></div>
            <span style={{ marginLeft: '12px' }}>Connecting to live stream...</span>
          </LoadingOverlay>
        )}
      </StreamArea>

      <StatusBar>
        <div>
          Stream: <ConnectionStatus connected={connected}>
            {connected ? 'Connected' : 'Disconnected'}
          </ConnectionStatus>
          {frameRate > 0 && ` | ${frameRate} FPS`}
        </div>
        
        <QualityControl>
          <span>Quality:</span>
          <QualitySlider
            type="range"
            min="10"
            max="100"
            value={quality}
            onChange={(e) => setQuality(e.target.value)}
          />
          <span>{quality}%</span>
        </QualityControl>
        
        {vncInfo && vncInfo.running && (
          <div>
            VNC: Port {vncInfo.port} | Display {vncInfo.display}
          </div>
        )}
      </StatusBar>
    </StreamContainer>
  );
};

export default LiveStreamViewer;
