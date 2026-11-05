#!/usr/bin/env python3
"""Start the backend server"""
import sys
import os
import traceback
import subprocess
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def kill_port_process(port):
    """Kill any process running on the specified port"""
    try:
        # Use netstat to find process on port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            # Extract PID from netstat output
            parts = result.stdout.strip().split()
            if parts:
                pid = parts[-1]
                print(f"[INFO] Found process {pid} on port {port}, killing it...")
                subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                time.sleep(1)  # Wait for port to be released
                print(f"[INFO] Port {port} cleaned up")
    except Exception as e:
        print(f"[WARN] Could not clean port {port}: {e}")

try:
    print("[INFO] Cleaning up port 8000...")
    kill_port_process(8000)
    
    from app.main import app
    import uvicorn
    print("[OK] Successfully imported app")
    print(f"[INFO] Starting backend server on http://127.0.0.1:8000")
    # Use reload=False to prevent multiprocessing issues
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info', reload=False)
except Exception as e:
    print(f"[ERROR] Error: {e}")
    traceback.print_exc()
    sys.exit(1)
