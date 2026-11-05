#!/usr/bin/env python
"""
CampaignCraft Playwright UI Test Runner - Simple Version
This script:
1. Starts backend server
2. Starts frontend server
3. Waits for them to be ready
4. Runs Playwright tests in headed mode with screenshots
"""

import subprocess
import time
import os
import sys
import signal
from pathlib import Path
import logging
import threading

# Configure logging with UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class SimpleTestRunner:
    def __init__(self):
        self.root = Path(__file__).parent
        self.backend_path = self.root / "backend"
        self.frontend_path = self.root / "frontend"
        self.logs_dir = self.root / "logs"
        
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        (self.logs_dir / "screenshots").mkdir(exist_ok=True, parents=True)
        
        self.backend_process = None
        self.frontend_process = None
        self.backend_ready = False
        self.frontend_ready = False
    
    def start_backend(self):
        """Start FastAPI backend"""
        logger.info("\n" + "="*70)
        logger.info("Starting FastAPI backend...")
        logger.info("="*70 + "\n")
        
        backend_log = self.logs_dir / "backend_runner.log"
        with open(backend_log, 'w') as f:
            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
                cwd=str(self.backend_path),
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=None  # Windows doesn't use preexec_fn
            )
        logger.info(f"Backend process started (PID: {self.backend_process.pid})")
    
    def start_frontend(self):
        """Start Vite frontend"""
        logger.info("Starting Vite frontend...")
        
        frontend_log = self.logs_dir / "frontend_runner.log"
        with open(frontend_log, 'w') as f:
            # Use shell=True on Windows to find npm
            self.frontend_process = subprocess.Popen(
                "npm run dev",
                cwd=str(self.frontend_path),
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True
            )
        logger.info(f"Frontend process started (PID: {self.frontend_process.pid})\n")
    
    def wait_for_services(self):
        """Wait for services to start"""
        logger.info("Waiting for services to be ready (up to 60 seconds)...\n")
        
        import urllib.request
        
        # Wait for backend
        logger.info("Checking backend...")
        for i in range(30):
            try:
                urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=2)
                logger.info("✓ Backend is ready\n")
                self.backend_ready = True
                break
            except:
                pass
            print(f"  Attempt {i+1}/30...", end='\r')
            time.sleep(2)
        
        if not self.backend_ready:
            logger.warning("Backend did not start, proceeding anyway...\n")
        
        time.sleep(2)
        
        # Wait for frontend
        logger.info("Checking frontend...")
        for i in range(30):
            try:
                urllib.request.urlopen("http://localhost:3000", timeout=2)
                logger.info("✓ Frontend is ready\n")
                self.frontend_ready = True
                break
            except:
                pass
            print(f"  Attempt {i+1}/30...", end='\r')
            time.sleep(2)
        
        if not self.frontend_ready:
            logger.warning("Frontend did not start, proceeding anyway...\n")
    
    def run_tests(self):
        """Run Playwright tests"""
        logger.info("="*70)
        logger.info("Running Playwright UI Tests - HEADED MODE")
        logger.info("="*70 + "\n")
        
        logger.info(f"Screenshots will be saved to: {self.logs_dir}/screenshots")
        logger.info(f"Test logs will be saved to: {self.logs_dir}/ui_tests.log\n")
        logger.info("Browser window will open - watch the tests execute...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "test_ui_headed.py", "-v", "-s"],
                cwd=str(self.backend_path),
                timeout=600
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return False
    
    def cleanup(self):
        """Clean up processes"""
        logger.info("\n[Cleanup] Stopping processes...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                self.frontend_process.kill()
        
        logger.info("Done")
    
    def run(self):
        """Run the test suite"""
        try:
            logger.info("\n" + "="*70)
            logger.info("CampaignCraft Playwright UI Test Suite")
            logger.info("="*70 + "\n")
            
            # Start services
            self.start_backend()
            time.sleep(2)
            self.start_frontend()
            
            # Wait for ready
            self.wait_for_services()
            
            # Run tests
            success = self.run_tests()
            
            # Results
            logger.info("\n" + "="*70)
            if success:
                logger.info("SUCCESS - All tests passed!")
            else:
                logger.info("Some tests failed - see output above")
            logger.info("="*70 + "\n")
            
            logger.info(f"Screenshots saved to: {self.logs_dir}/screenshots")
            logger.info(f"Logs saved to: {self.logs_dir}/\n")
            
            logger.info("Services still running for manual testing:")
            logger.info("  Backend:  http://127.0.0.1:8000")
            logger.info("  Frontend: http://localhost:3000")
            logger.info("  API Docs: http://127.0.0.1:8000/docs\n")
            
            logger.info("Press Ctrl+C to stop all services\n")
            
            # Keep running
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()


if __name__ == "__main__":
    runner = SimpleTestRunner()
    runner.run()
