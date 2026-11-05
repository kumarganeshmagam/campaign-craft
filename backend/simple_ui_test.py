"""
Simple UI Test for CampaignCraft Application
Tests the basic functionality of the UI in headed mode
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright
import time

class CampaignCraftUITest:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        
    async def test_backend_health(self):
        """Test if backend is responding"""
        print("[INFO] Testing backend health...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/docs", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        print("[PASS] Backend is healthy!")
                        return True
                    else:
                        print(f"[FAIL] Backend returned status {resp.status}")
                        return False
        except Exception as e:
            print(f"[FAIL] Backend health check failed: {e}")
            return False
    
    async def test_campaign_api(self):
        """Test the campaign API endpoint"""
        print("[INFO] Testing campaign API...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"topic": "AI automation in retail"}
                async with session.post(
                    f"{self.backend_url}/api/start-campaign",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "campaign_id" in data and "stream_url" in data:
                            print(f"[PASS] Campaign API works! ID: {data['campaign_id']}")
                            return True
                        else:
                            print("[FAIL] Campaign API response missing required fields")
                            return False
                    else:
                        print(f"[FAIL] Campaign API returned status {resp.status}")
                        return False
        except Exception as e:
            print(f"[FAIL] Campaign API test failed: {e}")
            return False
    
    async def test_frontend_ui(self):
        """Test the frontend UI with Playwright"""
        print("[INFO] Testing frontend UI...")
        
        async with async_playwright() as p:
            # Launch browser in headed mode
            browser = await p.chromium.launch(
                headless=False,  # Show browser window
                slow_mo=1000     # Slow down for visibility
            )
            
            try:
                context = await browser.new_context(
                    viewport={"width": 1400, "height": 900}
                )
                page = await context.new_page()
                
                # Navigate to frontend
                print(f"[INFO] Navigating to {self.frontend_url}")
                await page.goto(self.frontend_url, wait_until="networkidle", timeout=15000)
                
                # Take screenshot
                await page.screenshot(path="frontend_test.png", full_page=True)
                print("[INFO] Screenshot saved as frontend_test.png")
                
                # Check for main elements
                print("[INFO] Checking for UI elements...")
                
                # Check title
                title = await page.query_selector('h1')
                if title:
                    title_text = await title.text_content()
                    print(f"[PASS] Found title: {title_text}")
                else:
                    print("[FAIL] Main title not found")
                    return False
                
                # Check input field
                input_field = await page.query_selector('input[placeholder*="topic"], input[placeholder*="campaign"]')
                if input_field:
                    print("[PASS] Found campaign input field")
                else:
                    print("[FAIL] Campaign input field not found")
                    return False
                
                # Check start button
                start_button = await page.query_selector('button:has-text("Start Campaign"), button:has-text("Start")')
                if start_button:
                    print("[PASS] Found Start Campaign button")
                else:
                    print("[FAIL] Start Campaign button not found")
                    return False
                
                # Test input interaction
                print("[INFO] Testing input interaction...")
                await input_field.fill("AI automation test")
                await page.wait_for_timeout(1000)  # Wait 1 second
                
                input_value = await input_field.input_value()
                if input_value == "AI automation test":
                    print("[PASS] Input field works correctly")
                else:
                    print(f"[FAIL] Input field issue. Expected 'AI automation test', got '{input_value}'")
                    return False
                
                # Test button click (but don't wait for full campaign)
                print("[INFO] Testing button click...")
                await start_button.click()
                await page.wait_for_timeout(2000)  # Wait 2 seconds
                
                # Check if anything changed (loading state, etc.)
                loading_indicator = await page.query_selector('[class*="loading"], [class*="spinner"], .animate-spin')
                if loading_indicator:
                    print("[PASS] Button click triggered loading state")
                else:
                    print("[WARN] No loading indicator found, but button click registered")
                
                print("[PASS] Frontend UI test completed successfully!")
                return True
                
            except Exception as e:
                print(f"[FAIL] Frontend UI test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def run_all_tests(self):
        """Run all tests"""
        print("[START] CampaignCraft UI Tests")
        print("=" * 50)
        
        results = []
        
        # Test 1: Backend Health
        results.append(await self.test_backend_health())
        print()
        
        # Test 2: Campaign API
        results.append(await self.test_campaign_api())
        print()
        
        # Test 3: Frontend UI
        results.append(await self.test_frontend_ui())
        print()
        
        # Summary
        print("=" * 50)
        print("[SUMMARY] TEST RESULTS")
        print("=" * 50)
        
        test_names = ["Backend Health", "Campaign API", "Frontend UI"]
        for i, (name, result) in enumerate(zip(test_names, results)):
            status = "[PASS]" if result else "[FAIL]"
            print(f"{i+1}. {name}: {status}")
        
        passed = sum(results)
        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("[SUCCESS] All tests passed! CampaignCraft UI is working correctly.")
        else:
            print("[WARNING] Some tests failed. Check the output above for details.")
        
        return passed == total

async def main():
    """Main test runner"""
    tester = CampaignCraftUITest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)