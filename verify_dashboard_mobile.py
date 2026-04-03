import asyncio
from playwright.async_api import async_playwright, expect
import time

async def verify_dashboard():
    print("Starting playwright test...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Test mobile viewport width (e.g. iPhone SE)
        await page.set_viewport_size({"width": 375, "height": 667})

        try:
            print("Navigating to dashboard on mobile viewport...")
            await page.goto("http://localhost:8080/")
            # Wait for some content to load - text exact to avoid drawer issues
            await expect(page.locator("text='Dashboard'").first).to_be_visible(timeout=20000)

            # Wait a bit to let stats populate
            await page.wait_for_timeout(2000)

            print("Dashboard loaded successfully.")

            # We look for the main layout classes we replaced
            # Like grid-cols-1 or flex-col ensuring it takes effect

            # Let's take a screenshot for visual inspection
            await page.screenshot(path="dashboard_mobile.png", full_page=True)
            print("Saved mobile screenshot to dashboard_mobile.png")

            # Verify that flex directions and grids are present
            # We can't easily assert tailwind classes without javascript eval, so let's do that
            has_grid = await page.evaluate("() => document.querySelectorAll('.grid-cols-1').length > 0")
            has_flex_col = await page.evaluate("() => document.querySelectorAll('.flex-col').length > 0")

            if has_grid:
                print("Found responsive grid classes (.grid-cols-1).")
            else:
                print("Warning: .grid-cols-1 not found.")

            if has_flex_col:
                print("Found responsive flex classes (.flex-col).")
            else:
                print("Warning: .flex-col not found.")

        except Exception as e:
            print(f"Test failed: {e}")
            await page.screenshot(path="dashboard_mobile_error.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_dashboard())
