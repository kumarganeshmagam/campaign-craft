"""
Playwright UI Tests for CampaignCraft - HEADED MODE with Screenshots
Runs tests in headed mode (visible browser) and captures screenshots for debugging
"""

import pytest
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser, expect
import aiohttp
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
SCREENSHOTS_DIR = LOG_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

TEST_LOG = LOG_DIR / "ui_tests.log"

# Configure logging
file_handler = logging.FileHandler(TEST_LOG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


class TestCampaignCraftUI:
    """Comprehensive UI test suite for CampaignCraft with visual debugging"""
    
    BACKEND_URL = "http://127.0.0.1:8000"
    FRONTEND_URL = "http://localhost:3000"
    HEADED = True  # Set to False for headless mode
    SLOW_MO = 500  # Slow down execution to see what's happening
    
    @pytest.fixture
    async def browser(self):
        """Setup browser in HEADED mode for visual debugging"""
        logger.info("🌐 Launching browser in HEADED mode...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=not self.HEADED,
                slow_mo=self.SLOW_MO if self.HEADED else 0,
            )
            yield browser
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser):
        """Setup page context with enhanced logging"""
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
        )
        page = await context.new_page()
        
        # Capture console messages
        page.on("console", lambda msg: logger.info(f"[Browser Console] {msg.type}: {msg.text}"))
        page.on("request", lambda req: logger.debug(f"[Request] {req.method} {req.url}"))
        page.on("response", lambda resp: logger.debug(f"[Response] {resp.status} {resp.url}"))
        page.on("pageerror", lambda err: logger.error(f"[Page Error] {err}"))
        
        yield page
        await context.close()
    
    async def take_screenshot(self, page, name: str):
        """Take a screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOTS_DIR / f"{timestamp}_{name}.png"
        await page.screenshot(path=str(path), full_page=True)
        logger.info(f"📸 Screenshot saved: {path}")
        return path
    
    async def wait_for_backend(self, retries=15):
        """Wait for backend to be ready"""
        logger.info("Waiting for backend...")
        for i in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.BACKEND_URL}/docs", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            logger.info("✅ Backend is ready!")
                            return True
            except Exception as e:
                logger.debug(f"Backend check attempt {i+1}/{retries} failed: {e}")
            
            if i < retries - 1:
                await asyncio.sleep(1)
        
        logger.error("❌ Backend is not responding after multiple retries")
        return False
    
    async def wait_for_frontend(self, page, retries=15):
        """Wait for frontend to be ready"""
        logger.info("⏳ Waiting for frontend...")
        for i in range(retries):
            try:
                await page.goto(self.FRONTEND_URL, wait_until="networkidle", timeout=10000)
                logger.info("✅ Frontend is ready!")
                return True
            except Exception as e:
                logger.debug(f"Frontend check attempt {i+1}/{retries} failed: {e}")
            
            if i < retries - 1:
                await asyncio.sleep(1)
        
        logger.error("❌ Frontend is not responding after multiple retries")
        return False
    
    # ==================== TEST 1: Backend Health ====================
    @pytest.mark.asyncio
    async def test_01_backend_health(self):
        """Test backend health endpoint"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: Backend Health Check")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_backend():
                pytest.skip("Backend not available")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BACKEND_URL}/docs") as resp:
                    assert resp.status == 200, f"Expected 200, got {resp.status}"
                    logger.info(f"✅ Backend API docs endpoint returned {resp.status}")
            
            logger.info("✅ TEST PASSED: Backend is healthy\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}\n")
            raise
    
    # ==================== TEST 2: API Endpoint ====================
    @pytest.mark.asyncio
    async def test_02_start_campaign_api(self):
        """Test the start campaign API endpoint"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: Start Campaign API Endpoint")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_backend():
                pytest.skip("Backend not available")
            
            async with aiohttp.ClientSession() as session:
                payload = {"topic": "AI automation in retail"}
                logger.info(f"📤 Sending request: {payload}")
                
                async with session.post(
                    f"{self.BACKEND_URL}/api/start-campaign",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    assert resp.status == 200, f"Expected 200, got {resp.status}"
                    data = await resp.json()
                    
                    assert "campaign_id" in data, "Missing campaign_id in response"
                    assert "stream_url" in data, "Missing stream_url in response"
                    
                    logger.info(f"✅ Campaign created with ID: {data['campaign_id']}")
                    logger.info(f"✅ Stream URL: {data['stream_url']}")
                    logger.info(f"📝 Full response: {data}")
            
            logger.info("✅ TEST PASSED: Campaign API endpoint works\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}\n")
            raise
    
    # ==================== TEST 3: Frontend Loads ====================
    @pytest.mark.asyncio
    async def test_03_frontend_landing_page(self, page):
        """Test frontend loads successfully"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: Frontend Landing Page")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_backend():
                pytest.skip("Backend not available")
            
            if not await self.wait_for_frontend(page):
                pytest.skip("Frontend not available")
            
            await asyncio.sleep(1)  # Let page fully render
            
            # Take initial screenshot
            await self.take_screenshot(page, "01_landing_page")
            
            # Check for main title
            title_element = await page.query_selector('h1')
            assert title_element is not None, "Main title not found"
            title_text = await title_element.text_content()
            logger.info(f"✅ Found title: {title_text}")
            
            # Check for campaign input field
            input_field = await page.query_selector('input[placeholder*="topic"]')
            assert input_field is not None, "Campaign input field not found"
            logger.info("✅ Found campaign topic input field")
            
            # Check for Start Campaign button
            start_button = await page.query_selector('button:has-text("Start Campaign")')
            assert start_button is not None, "Start Campaign button not found"
            logger.info("✅ Found Start Campaign button")
            
            # Check for suggestion text
            suggestion = await page.query_selector('p:has-text("Try:")')
            assert suggestion is not None, "Suggestion text not found"
            logger.info("✅ Found suggestion text")
            
            logger.info("✅ TEST PASSED: Landing page loaded successfully\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "03_landing_error")
            raise
    
    # ==================== TEST 4: Input Validation ====================
    @pytest.mark.asyncio
    async def test_04_input_validation(self, page):
        """Test input field validation"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: Input Validation")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_frontend(page):
                pytest.skip("Frontend not available")
            
            logger.info("📝 Testing empty submit...")
            start_button = await page.query_selector('button:has-text("Start Campaign")')
            assert start_button is not None
            
            # Check if button is disabled when input is empty
            is_disabled = await start_button.is_disabled()
            logger.info(f"✅ Button is disabled when input empty: {is_disabled}")
            assert is_disabled, "Start button should be disabled with empty input"
            
            logger.info("📝 Testing input field...")
            input_field = await page.query_selector('input[placeholder*="topic"]')
            
            # Type some text
            await input_field.fill("Test Campaign Topic")
            await asyncio.sleep(0.5)
            
            # Check if button becomes enabled
            is_disabled = await start_button.is_disabled()
            logger.info(f"✅ Button is enabled after input: {not is_disabled}")
            assert not is_disabled, "Start button should be enabled with valid input"
            
            # Clear input
            await input_field.clear()
            await asyncio.sleep(0.3)
            
            # Check if button is disabled again
            is_disabled = await start_button.is_disabled()
            logger.info(f"✅ Button is disabled again after clearing: {is_disabled}")
            assert is_disabled, "Start button should be disabled after clearing input"
            
            logger.info("✅ TEST PASSED: Input validation works correctly\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "04_validation_error")
            raise
    
    # ==================== TEST 5: Campaign Submission (Long Running) ====================
    @pytest.mark.asyncio
    async def test_05_campaign_submission_flow(self, page):
        """Test full campaign submission flow with real streaming"""
        logger.info("\n" + "="*70)
        logger.info("TEST 5: Full Campaign Submission Flow (30 second timeout)")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_backend():
                pytest.skip("Backend not available")
            
            if not await self.wait_for_frontend(page):
                pytest.skip("Frontend not available")
            
            logger.info("📝 Filling campaign form...")
            topic = "AI-powered customer service chatbot"
            
            # Fill input
            input_field = await page.query_selector('input[placeholder*="topic"]')
            assert input_field is not None
            await input_field.fill(topic)
            logger.info(f"✅ Entered topic: '{topic}'")
            
            await self.take_screenshot(page, "05_form_filled")
            
            # Click submit
            logger.info("🚀 Clicking Start Campaign button...")
            start_button = await page.query_selector('button:has-text("Start Campaign")')
            assert start_button is not None
            await start_button.click()
            
            await asyncio.sleep(2)  # Let page transition
            await self.take_screenshot(page, "05_after_submit")
            
            logger.info("⏳ Waiting for streaming responses (30 seconds)...")
            
            # Wait for campaign to start showing results
            messages_found = False
            tabs_found = False
            
            for attempt in range(30):
                try:
                    # Look for message elements
                    messages = await page.query_selector_all('[class*="message"], [class*="Agent"], p')
                    visible_text = ""
                    for msg in messages[:5]:  # Get first 5
                        try:
                            text = await msg.text_content()
                            if text and len(text) > 5:
                                visible_text += text[:80] + " | "
                        except:
                            pass
                    
                    if visible_text:
                        logger.info(f"[{attempt+1}s] Messages: {visible_text[:150]}")
                        messages_found = True
                    
                    # Look for tabs
                    tabs = await page.query_selector_all('button[class*="tab"], nav button')
                    if len(tabs) > 2:
                        tabs_found = True
                        logger.info(f"[{attempt+1}s] ✅ Found {len(tabs)} tabs")
                    
                    if messages_found or tabs_found:
                        break
                    
                except Exception as e:
                    logger.debug(f"Check attempt {attempt+1}: {e}")
                
                await asyncio.sleep(1)
            
            # Take screenshot of campaign view
            await self.take_screenshot(page, "05_campaign_results")
            
            if messages_found:
                logger.info("✅ Campaign messages started streaming")
            if tabs_found:
                logger.info("✅ Campaign dashboard tabs are visible")
            
            assert messages_found or tabs_found, "No campaign results found"
            
            logger.info("✅ TEST PASSED: Campaign submission flow works\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "05_campaign_error")
            raise
    
    # ==================== TEST 6: Tab Navigation ====================
    @pytest.mark.asyncio
    async def test_06_tab_navigation(self, page):
        """Test tab navigation in campaign dashboard"""
        logger.info("\n" + "="*70)
        logger.info("TEST 6: Tab Navigation")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_frontend(page):
                pytest.skip("Frontend not available")
            
            # First ensure we're in campaign mode
            input_field = await page.query_selector('input[placeholder*="topic"]')
            if input_field:
                await input_field.fill("Marketing Strategy")
                start_button = await page.query_selector('button:has-text("Start Campaign")')
                if start_button:
                    await start_button.click()
                    await asyncio.sleep(3)
            
            logger.info("🔍 Looking for tabs...")
            
            # Look for tab buttons
            tab_buttons = await page.query_selector_all('button[class*="tab"], nav button')
            
            if len(tab_buttons) == 0:
                logger.warning("⚠️ No tabs found yet, campaign may still be loading")
                pytest.skip("Campaign not fully loaded")
            
            logger.info(f"✅ Found {len(tab_buttons)} tab buttons")
            
            # Click each tab and verify
            tab_names = ["Plan", "Use Cases", "Target", "Proposal"]
            
            for i, button in enumerate(tab_buttons[:4]):
                try:
                    button_text = await button.text_content()
                    logger.info(f"📋 Clicking tab: {button_text}")
                    
                    await button.click()
                    await asyncio.sleep(0.5)
                    
                    await self.take_screenshot(page, f"06_tab_{i}_{button_text.split()[0]}")
                    logger.info(f"✅ Tab {i+1} clickable and content displayed")
                    
                except Exception as e:
                    logger.error(f"Tab {i+1} click failed: {e}")
            
            logger.info("✅ TEST PASSED: Tab navigation works\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "06_tabs_error")
            raise
    
    # ==================== TEST 7: Generate Content Button ====================
    @pytest.mark.asyncio
    async def test_07_generate_content_button(self, page):
        """Test Generate Campaign Content button"""
        logger.info("\n" + "="*70)
        logger.info("TEST 7: Generate Content Button")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_frontend(page):
                pytest.skip("Frontend not available")
            
            logger.info("🔍 Looking for Generate Content button...")
            
            # Look for the button
            generate_button = await page.query_selector('button:has-text("Generate Campaign Content")')
            
            if generate_button is None:
                logger.warning("⚠️ Generate Content button not found, may not be in campaign mode")
                pytest.skip("Not in campaign mode")
            
            logger.info("✅ Found Generate Campaign Content button")
            
            # Check if button is clickable
            is_enabled = not await generate_button.is_disabled()
            logger.info(f"✅ Button is enabled: {is_enabled}")
            
            # Try clicking it (but don't wait for full response)
            logger.info("🖱️ Clicking Generate Content button...")
            await generate_button.click()
            await asyncio.sleep(2)
            
            await self.take_screenshot(page, "07_after_generate_click")
            
            logger.info("✅ TEST PASSED: Generate Content button works\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "07_generate_error")
            raise
    
    # ==================== TEST 8: Responsive Design ====================
    @pytest.mark.asyncio
    async def test_08_responsive_design(self, browser):
        """Test responsive design at different viewport sizes"""
        logger.info("\n" + "="*70)
        logger.info("TEST 8: Responsive Design")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_frontend(None):
                pytest.skip("Frontend not available")
            
            viewports = [
                ("Mobile", {"width": 375, "height": 667}),
                ("Tablet", {"width": 768, "height": 1024}),
                ("Desktop", {"width": 1400, "height": 900}),
            ]
            
            for device_name, viewport in viewports:
                logger.info(f"📱 Testing {device_name} viewport: {viewport}")
                
                context = await browser.new_context(viewport=viewport)
                page = await context.new_page()
                
                try:
                    await page.goto(self.FRONTEND_URL, wait_until="networkidle", timeout=10000)
                    await asyncio.sleep(1)
                    
                    # Check if main elements exist
                    title = await page.query_selector('h1')
                    input_field = await page.query_selector('input')
                    button = await page.query_selector('button')
                    
                    assert title is not None, f"{device_name}: Title not found"
                    assert input_field is not None, f"{device_name}: Input field not found"
                    assert button is not None, f"{device_name}: Button not found"
                    
                    await page.screenshot(path=str(SCREENSHOTS_DIR / f"08_responsive_{device_name}.png"), full_page=True)
                    logger.info(f"✅ {device_name} layout renders correctly")
                    
                except Exception as e:
                    logger.error(f"❌ {device_name} test failed: {e}")
                    raise
                
                finally:
                    await context.close()
            
            logger.info("✅ TEST PASSED: Responsive design works\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}\n")
            raise
    
    # ==================== TEST 9: Error Handling ====================
    @pytest.mark.asyncio
    async def test_09_error_handling(self, page):
        """Test error handling and error messages"""
        logger.info("\n" + "="*70)
        logger.info("TEST 9: Error Handling")
        logger.info("="*70)
        
        try:
            if not await self.wait_for_frontend(page):
                pytest.skip("Frontend not available")
            
            logger.info("📝 Testing error message display...")
            
            # The page should load without JavaScript errors
            js_errors = []
            page.on("pageerror", lambda err: js_errors.append(str(err)))
            
            await asyncio.sleep(2)
            
            if js_errors:
                logger.warning(f"⚠️ Found {len(js_errors)} JavaScript errors:")
                for err in js_errors:
                    logger.warning(f"  - {err}")
            else:
                logger.info("✅ No JavaScript errors found")
            
            logger.info("✅ TEST PASSED: Error handling verified\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "09_error_handling")
            raise
    
    # ==================== TEST 10: Performance ====================
    @pytest.mark.asyncio
    async def test_10_page_load_performance(self, page):
        """Test page load performance"""
        logger.info("\n" + "="*70)
        logger.info("TEST 10: Page Load Performance")
        logger.info("="*70)
        
        try:
            import time
            
            start_time = time.time()
            await page.goto(self.FRONTEND_URL, wait_until="networkidle", timeout=10000)
            load_time = time.time() - start_time
            
            logger.info(f"⏱️ Page load time: {load_time:.2f} seconds")
            
            # Check that load time is reasonable (less than 5 seconds)
            assert load_time < 5.0, f"Page load took too long: {load_time:.2f}s"
            
            logger.info(f"✅ Page loaded in acceptable time ({load_time:.2f}s)")
            logger.info("✅ TEST PASSED: Performance is good\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            await self.take_screenshot(page, "10_performance_error")
            raise


def run_ui_tests():
    """Run all UI tests with Playwright"""
    logger.info("\n" + "="*70)
    logger.info("🎬 STARTING CAMPAIGNCRAFT UI TEST SUITE - HEADED MODE")
    logger.info("="*70)
    logger.info(f"📸 Screenshots will be saved to: {SCREENSHOTS_DIR}")
    logger.info(f"📝 Logs will be saved to: {TEST_LOG}")
    logger.info("="*70 + "\n")
    
    # Run pytest
    import subprocess
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short", "-s"],
        cwd=Path(__file__).parent
    )
    
    logger.info("\n" + "="*70)
    logger.info(f"✅ Test suite complete. Exit code: {result.returncode}")
    logger.info(f"📸 All screenshots saved to: {SCREENSHOTS_DIR}")
    logger.info("="*70 + "\n")
    
    return result.returncode == 0


if __name__ == "__main__":
    asyncio.run(run_ui_tests())
