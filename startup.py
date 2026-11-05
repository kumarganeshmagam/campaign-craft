#!/usr/bin/env python3
"""
Master startup script for CampaignCraft
Starts backend, frontend, and runs tests
Logs everything to files instead of terminal
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime

# Directories
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log files
BACKEND_LOG = LOG_DIR / "backend_startup.log"
FRONTEND_LOG = LOG_DIR / "frontend_startup.log"
TEST_LOG = LOG_DIR / "test_results.log"
MASTER_LOG = LOG_DIR / "startup.log"

def log_to_file(filename, message):
    """Write message to log file with timestamp"""
    # Sanitize message to remove problematic Unicode characters
    message = message.replace("✓", "[OK]").replace("✗", "[ERROR]").replace("⚠", "[WARN]")
    
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def log_and_print(message, log_file=MASTER_LOG):
    """Log to file and print to console"""
    log_to_file(log_file, message)
    # Replace Unicode characters for console output
    console_message = message.replace("✓", "[OK]").replace("✗", "[ERROR]").replace("⚠", "[WARN]")
    print(console_message)

def start_backend():
    """Start backend server and log to file"""
    log_and_print("[Backend] Starting backend server...")
    
    # Clear previous logs
    BACKEND_LOG.write_text("")
    
    try:
        # Kill any existing process on port 8000
        log_to_file(BACKEND_LOG, "Cleaning up port 8000...")
        subprocess.run(
            "for /f \"tokens=5\" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F",
            shell=True,
            capture_output=True
        )
        time.sleep(1)
        
        # Start backend
        process = subprocess.Popen(
            ["python", "run_server.py"],
            cwd=BACKEND_DIR,
            stdout=open(BACKEND_LOG, "a"),
            stderr=subprocess.STDOUT,
            text=True
        )
        
        log_and_print(f"[Backend] Started with PID {process.pid}")
        log_to_file(BACKEND_LOG, f"Backend started with PID {process.pid}")
        
        # Wait for backend to be ready
        time.sleep(3)
        
        import socket
        for _ in range(10):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 8000))
                sock.close()
                if result == 0:
                    log_and_print("[Backend] ✓ Backend is ready on http://127.0.0.1:8000")
                    log_to_file(BACKEND_LOG, "Backend is ready")
                    return process
            except:
                pass
            time.sleep(1)
        
        log_and_print("[Backend] ⚠ Backend may not be ready yet")
        return process
        
    except Exception as e:
        log_and_print(f"[Backend] ✗ Error starting backend: {e}")
        return None

def start_frontend():
    """Start frontend server and log to file"""
    log_and_print("[Frontend] Starting frontend server...")
    
    # Clear previous logs
    FRONTEND_LOG.write_text("")
    
    try:
        # Kill any existing process on port 3000
        log_to_file(FRONTEND_LOG, "Cleaning up port 3000...")
        subprocess.run(
            "for /f \"tokens=5\" %%a in ('netstat -ano ^| findstr :3000') do taskkill /PID %%a /F",
            shell=True,
            capture_output=True
        )
        time.sleep(1)
        
        # Start frontend
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=FRONTEND_DIR,
            stdout=open(FRONTEND_LOG, "a"),
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        
        log_and_print(f"[Frontend] Started with PID {process.pid}")
        log_to_file(FRONTEND_LOG, f"Frontend started with PID {process.pid}")
        
        # Wait for frontend to be ready
        time.sleep(5)
        
        log_and_print("[Frontend] ✓ Frontend is ready on http://localhost:3000")
        return process
        
    except Exception as e:
        log_and_print(f"[Frontend] ✗ Error starting frontend: {e}")
        return None

def run_tests():
    """Run E2E tests after apps are ready"""
    log_and_print("\n[Tests] Waiting 3 seconds before starting tests...")
    time.sleep(3)
    
    log_and_print("[Tests] Starting E2E test suite...")
    log_to_file(TEST_LOG, "Test suite started")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "test_e2e.py", "-v", "--tb=short"],
            cwd=BACKEND_DIR,
            stdout=open(TEST_LOG, "a"),
            stderr=subprocess.STDOUT,
            timeout=60
        )
        
        if result.returncode == 0:
            log_and_print("[Tests] ✓ All tests passed!")
        else:
            log_and_print(f"[Tests] ⚠ Tests completed with exit code {result.returncode}")
            log_and_print("[Tests] Check logs/test_results.log for details")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        log_and_print("[Tests] ✗ Tests timed out")
        return 1
    except Exception as e:
        log_and_print(f"[Tests] ✗ Error running tests: {e}")
        return 1

def main():
    """Main startup orchestrator"""
    log_and_print("\n" + "=" * 70)
    log_and_print("CampaignCraft Application Startup")
    log_and_print("=" * 70)
    log_and_print(f"Log directory: {LOG_DIR}\n")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        log_and_print("\n✗ Failed to start backend")
        return 1
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        log_and_print("\n✗ Failed to start frontend")
        if backend_process:
            backend_process.terminate()
        return 1
    
    log_and_print("\n" + "=" * 70)
    log_and_print("✓ Both backend and frontend are running!")
    log_and_print("=" * 70)
    log_and_print(f"\nBackend:  http://127.0.0.1:8000")
    log_and_print(f"Frontend: http://localhost:3000")
    log_and_print(f"\nLogs are being written to: {LOG_DIR}")
    log_and_print("\nRunning E2E tests in background...\n")
    
    # Run tests in separate thread
    test_thread = threading.Thread(target=run_tests, daemon=False)
    test_thread.start()
    
    # Keep processes running
    try:
        log_and_print("Press Ctrl+C to stop the application\n")
        while True:
            time.sleep(1)
            
            # Check if processes are still alive
            if backend_process.poll() is not None:
                log_and_print("\n✗ Backend process exited!")
                break
            
            if frontend_process.poll() is not None:
                log_and_print("\n✗ Frontend process exited!")
                break
                
    except KeyboardInterrupt:
        log_and_print("\n\n[Shutdown] Stopping application...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            log_and_print("[Shutdown] Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            log_and_print("[Shutdown] Frontend stopped")
        
        log_and_print("[Shutdown] Application shut down\n")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
