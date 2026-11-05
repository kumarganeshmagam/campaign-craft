"""
Debug UI Test - Check what's happening after button click
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        
        try:
            context = await browser.new_context(viewport={"width": 1400, "height": 900})
            page = await context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"[BROWSER] {msg.type}: {msg.text}"))
            page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
            
            print("[INFO] Navigating to frontend...")
            await page.goto("http://localhost:3000", wait_until="networkidle")
            
            print("[INFO] Taking initial screenshot...")
            await page.screenshot(path="debug_01_initial.png", full_page=True)
            
            # Fill input and click button
            input_field = await page.query_selector('input[placeholder*="topic"]')
            await input_field.fill("Test campaign")
            
            print("[INFO] Clicking start button...")
            start_button = await page.query_selector('button:has-text("Start Campaign")')
            await start_button.click()
            
            # Wait and see what happens
            print("[INFO] Waiting 5 seconds to see what happens...")
            await page.wait_for_timeout(5000)
            
            await page.screenshot(path="debug_02_after_click.png", full_page=True)
            
            # Check page content
            page_content = await page.content()
            print(f"[INFO] Page contains 'Campaign:': {'Campaign:' in page_content}")
            print(f"[INFO] Page contains 'Starting': {'Starting' in page_content}")
            print(f"[INFO] Page contains 'ChatUI': {'ChatUI' in page_content}")
            
            # Check for specific elements
            campaign_header = await page.query_selector('h2')
            if campaign_header:
                header_text = await campaign_header.text_content()
                print(f"[INFO] Found h2 element: {header_text}")
            
            # Check for any error messages
            error_elements = await page.query_selector_all('[class*="error"], .error')
            if error_elements:
                for error in error_elements:
                    error_text = await error.text_content()
                    print(f"[ERROR] Found error: {error_text}")
            
            # Wait longer to see if anything loads
            print("[INFO] Waiting 10 more seconds...")
            await page.wait_for_timeout(10000)
            
            await page.screenshot(path="debug_03_after_wait.png", full_page=True)
            
            # Check again
            page_content = await page.content()
            print(f"[INFO] After wait - Page contains 'Campaign:': {'Campaign:' in page_content}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_ui())