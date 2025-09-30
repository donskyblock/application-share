import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(process.env.REACT_APP_SERVER_URL || 'http://localhost:3000');
    
    newSocket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    newSocket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const joinApplication = (appId) => {
    if (socket) {
      socket.emit('join_application', { app_id: appId });
    }
  };

  const leaveApplication = () => {
    if (socket) {
      socket.emit('leave_application');
    }
  };

  const sendMouseEvent = (eventType, x, y, button = 1) => {
    if (socket) {
      socket.emit('mouse_event', {
        type: eventType,
        x,
        y,
        button
      });
    }
  };

  const sendKeyboardEvent = (key, modifiers = []) => {
    if (socket) {
      socket.emit('keyboard_event', {
        key,
        modifiers
      });
    }
  };

  const value = {
    socket,
    connected,
    joinApplication,
    leaveApplication,
    sendMouseEvent,
    sendKeyboardEvent
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};
