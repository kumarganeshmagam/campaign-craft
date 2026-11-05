#!/usr/bin/env python
"""
CampaignCraft UI Testing Runner
Starts backend, frontend, and runs Playwright tests in headed mode
"""

import subprocess
import time
import os
import sys
import signal
from pathlib import Path
import shutil
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UITestRunner:
    def __init__(self):
        self.root = Path(__file__).parent
        self.backend_path = self.root / "backend"
        self.frontend_path = self.root / "frontend"
        self.logs_dir = self.root / "logs"
        self.screenshots_dir = self.logs_dir / "screenshots"
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        self.screenshots_dir.mkdir(exist_ok=True, parents=True)
        
        self.backend_process = None
        self.frontend_process = None
    
    def cleanup_ports(self):
        """Kill any existing processes on ports 8000 and 3000"""
        logger.info("🧹 Cleaning up old processes...")
        
        try:
            # Windows-specific
            os.system("taskkill /F /IM python.exe /T 2>nul")
            os.system("taskkill /F /IM node.exe /T 2>nul")
            time.sleep(1)
            logger.info("✅ Cleanup complete")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")
    
    def start_backend(self):
        """Start FastAPI backend"""
        logger.info("\n" + "="*70)
        logger.info("🚀 STARTING BACKEND SERVER")
        logger.info("="*70)
        
        try:
            backend_log = self.logs_dir / "backend_startup.log"
            logger.info(f"Backend output → {backend_log}")
            
            with open(backend_log, 'w') as f:
                self.backend_process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
                    cwd=str(self.backend_path),
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            logger.info(f"✅ Backend process started (PID: {self.backend_process.pid})")
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            raise
    
    def start_frontend(self):
        """Start Vite frontend"""
        logger.info("\n" + "="*70)
        logger.info("🚀 STARTING FRONTEND SERVER")
        logger.info("="*70)
        
        try:
            frontend_log = self.logs_dir / "frontend_startup.log"
            logger.info(f"Frontend output → {frontend_log}")
            
            # Check if node_modules exists
            if not (self.frontend_path / "node_modules").exists():
                logger.info("📦 Installing frontend dependencies...")
                subprocess.run(
                    ["npm", "install", "--legacy-peer-deps"],
                    cwd=str(self.frontend_path),
                    check=True,
                    capture_output=True
                )
                logger.info("✅ Dependencies installed")
            
            with open(frontend_log, 'w') as f:
                self.frontend_process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=str(self.frontend_path),
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            logger.info(f"✅ Frontend process started (PID: {self.frontend_process.pid})")
            time.sleep(4)
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            raise
    
    def wait_for_services(self, max_retries=15):
        """Wait for services to be ready"""
        logger.info("\n" + "="*70)
        logger.info("⏳ WAITING FOR SERVICES")
        logger.info("="*70)
        
        import urllib.request
        
        backend_ready = False
        frontend_ready = False
        
        # Check backend
        logger.info("Checking backend (http://127.0.0.1:8000/docs)...")
        for i in range(max_retries):
            try:
                response = urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=2)
                if response.status == 200:
                    logger.info("✅ Backend is ready")
                    backend_ready = True
                    break
            except Exception as e:
                logger.debug(f"Attempt {i+1}/{max_retries}: {e}")
            
            time.sleep(1)
        
        # Check frontend
        logger.info("Checking frontend (http://localhost:3000)...")
        for i in range(max_retries):
            try:
                response = urllib.request.urlopen("http://localhost:3000", timeout=2)
                if response.status == 200:
                    logger.info("✅ Frontend is ready")
                    frontend_ready = True
                    break
            except Exception as e:
                logger.debug(f"Attempt {i+1}/{max_retries}: {e}")
            
            time.sleep(1)
        
        if not backend_ready:
            logger.warning("⚠️ Backend may not be fully ready")
        if not frontend_ready:
            logger.warning("⚠️ Frontend may not be fully ready")
        
        return backend_ready and frontend_ready
    
    def run_tests(self):
        """Run Playwright tests"""
        logger.info("\n" + "="*70)
        logger.info("🎬 RUNNING PLAYWRIGHT UI TESTS - HEADED MODE")
        logger.info("="*70)
        
        logger.info(f"📸 Screenshots → {self.screenshots_dir}")
        logger.info(f"📝 Test log → {self.logs_dir / 'ui_tests.log'}")
        logger.info("🌐 Opening browser window to watch tests...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "test_ui_headed.py", "-v", "-s", "--tb=short"],
                cwd=str(self.backend_path),
                timeout=600
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Tests timed out after 10 minutes")
            return False
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    def run(self):
        """Run the full test suite"""
        logger.info("\n" + "="*70)
        logger.info("🎯 CAMPAIGNCRAFT UI TEST SUITE")
        logger.info("="*70)
        
        try:
            # Cleanup
            self.cleanup_ports()
            
            # Start services
            self.start_backend()
            self.start_frontend()
            
            # Wait for ready
            self.wait_for_services()
            
            # Run tests
            success = self.run_tests()
            
            # Results
            logger.info("\n" + "="*70)
            if success:
                logger.info("✅ ALL TESTS PASSED!")
            else:
                logger.info("❌ SOME TESTS FAILED")
            logger.info("="*70)
            
            logger.info(f"\n📸 Screenshots: {self.screenshots_dir}")
            logger.info("📝 Check logs in: logs/")
            logger.info("\n✨ Services still running for manual testing:")
            logger.info("  Backend:  http://127.0.0.1:8000")
            logger.info("  Frontend: http://localhost:3000")
            logger.info("  API Docs: http://127.0.0.1:8000/docs")
            logger.info("\nPress Ctrl+C to stop all services\n")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\n⏹️  Shutting down...")
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup processes"""
        logger.info("🧹 Cleaning up...")
        
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
        
        os.system("taskkill /F /IM python.exe /T 2>nul")
        os.system("taskkill /F /IM node.exe /T 2>nul")
        
        logger.info("✅ Cleanup complete")


if __name__ == "__main__":
    runner = UITestRunner()
    runner.run()
