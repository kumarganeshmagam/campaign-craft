"""
Playwright tests for CampaignCraft
Tests the full campaign flow from UI to backend
"""

import pytest
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser
import aiohttp
import time

logger = logging.getLogger(__name__)

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
TEST_LOG = LOG_DIR / "tests.log"

# Configure logging
file_handler = logging.FileHandler(TEST_LOG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


class TestCampaignCraft:
    """Test suite for CampaignCraft application"""
    
    BACKEND_URL = "http://127.0.0.1:8000"
    FRONTEND_URL = "http://localhost:3000"
    
    @pytest.fixture
    async def browser(self):
        """Setup browser for testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            yield browser
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser):
        """Setup page context"""
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture console messages
        page.on("console", lambda msg: logger.info(f"[Browser Console] {msg.type}: {msg.text}"))
        
        yield page
        await context.close()
    
    async def wait_for_backend(self, retries=10):
        """Wait for backend to be ready"""
        for i in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.BACKEND_URL}/docs") as resp:
                        if resp.status == 200:
                            logger.info("✓ Backend is ready")
                            return True
            except:
                pass
            
            if i < retries - 1:
                logger.info(f"Waiting for backend... ({i+1}/{retries})")
                await asyncio.sleep(1)
        
        logger.error("✗ Backend is not responding")
        return False
    
    async def wait_for_frontend(self, page, retries=10):
        """Wait for frontend to be ready"""
        for i in range(retries):
            try:
                await page.goto(self.FRONTEND_URL, wait_until="networkidle", timeout=5000)
                logger.info("✓ Frontend is ready")
                return True
            except:
                pass
            
            if i < retries - 1:
                logger.info(f"Waiting for frontend... ({i+1}/{retries})")
                await asyncio.sleep(1)
        
        logger.error("✗ Frontend is not responding")
        return False
    
    @pytest.mark.asyncio
    async def test_backend_health(self):
        """Test backend health endpoint"""
        logger.info("=" * 60)
        logger.info("TEST: Backend Health Check")
        logger.info("=" * 60)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BACKEND_URL}/docs") as resp:
                    assert resp.status == 200
                    logger.info(f"✓ Backend returned status {resp.status}")
                    return True
        except Exception as e:
            logger.error(f"✗ Backend health check failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_start_campaign_endpoint(self):
        """Test the start campaign API endpoint"""
        logger.info("=" * 60)
        logger.info("TEST: Start Campaign Endpoint")
        logger.info("=" * 60)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"topic": "AI automation tools"}
                logger.info(f"Sending request: {payload}")
                
                async with session.post(
                    f"{self.BACKEND_URL}/api/start-campaign",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    assert resp.status == 200
                    data = await resp.json()
                    
                    assert "campaign_id" in data
                    assert "stream_url" in data
                    
                    logger.info(f"✓ Campaign started: {data['campaign_id']}")
                    logger.info(f"✓ Stream URL: {data['stream_url']}")
                    return True
                    
        except Exception as e:
            logger.error(f"✗ Campaign endpoint test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_frontend_loads(self, page):
        """Test frontend loads successfully"""
        logger.info("=" * 60)
        logger.info("TEST: Frontend Load")
        logger.info("=" * 60)
        
        try:
            if not await self.wait_for_backend():
                logger.warning("Backend not ready, skipping frontend test")
                return False
            
            if not await self.wait_for_frontend(page):
                logger.warning("Frontend not ready")
                return False
            
            # Check for main elements
            title = await page.title()
            logger.info(f"✓ Page title: {title}")
            
            # Check for campaign input
            input_field = await page.query_selector('input[placeholder*="topic"]')
            assert input_field is not None
            logger.info("✓ Found campaign topic input field")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Frontend load test failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path=str(LOG_DIR / "frontend_error.png"))
            return False
    
    @pytest.mark.asyncio
    async def test_campaign_submission(self, page):
        """Test submitting a campaign from frontend"""
        logger.info("=" * 60)
        logger.info("TEST: Campaign Submission Flow")
        logger.info("=" * 60)
        
        try:
            if not await self.wait_for_backend():
                logger.warning("Backend not ready")
                return False
            
            if not await self.wait_for_frontend(page):
                logger.warning("Frontend not ready")
                return False
            
            logger.info("Filling campaign topic...")
            topic = "AI automation for small businesses"
            
            # Find input field
            input_field = await page.query_selector('input[placeholder*="topic"]')
            assert input_field is not None
            
            # Type topic
            await input_field.fill(topic)
            logger.info(f"✓ Entered topic: {topic}")
            
            # Find and click submit button
            submit_button = await page.query_selector('button:has-text("Start Campaign")')
            assert submit_button is not None
            
            logger.info("Clicking 'Start Campaign' button...")
            await submit_button.click()
            
            # Wait for response
            await asyncio.sleep(2)
            
            # Check if messages started appearing
            messages = await page.query_selector_all('[class*="message"]')
            logger.info(f"✓ Received {len(messages)} messages")
            
            # Wait a bit more for stream data
            await asyncio.sleep(3)
            
            messages = await page.query_selector_all('[class*="message"]')
            logger.info(f"✓ Total messages received: {len(messages)}")
            
            if len(messages) > 0:
                first_message = await messages[0].text_content()
                logger.info(f"✓ First message: {first_message[:100]}...")
                return True
            else:
                logger.warning("⚠ No messages received")
                return False
                
        except Exception as e:
            logger.error(f"✗ Campaign submission test failed: {e}")
            await page.screenshot(path=str(LOG_DIR / "campaign_error.png"))
            return False


def run_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("Starting CampaignCraft Test Suite")
    logger.info("=" * 60 + "\n")
    
    # Run pytest
    import subprocess
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        cwd=Path(__file__).parent
    )
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Test run complete. Exit code: {result.returncode}")
    logger.info("=" * 60 + "\n")
    
    return result.returncode == 0


if __name__ == "__main__":
    asyncio.run(run_tests())
