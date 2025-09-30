#!/usr/bin/env python3
"""
Development server script for Application Share
Runs both the FastAPI backend and React frontend concurrently
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server"""
    print("🐍 Starting FastAPI backend server...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend server error: {e}")

def run_frontend():
    """Run the React frontend development server"""
    print("⚛️  Starting React frontend server...")
    try:
        os.chdir("client")
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend server error: {e}")

def main():
    """Main function to run both servers"""
    print("🚀 Starting Application Share Development Servers...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the application-share root directory")
        sys.exit(1)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("📝 Creating .env file from template...")
        if Path("env.example").exists():
            subprocess.run(["cp", "env.example", ".env"])
            print("⚠️  Please edit .env file with your configuration")
        else:
            print("❌ env.example file not found")
            sys.exit(1)
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
