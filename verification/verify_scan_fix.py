import time
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to Scan Page
        page.goto("http://localhost:8080/scan")

        # Wait for page to load
        time.sleep(2)
        page.wait_for_selector('text=Recent Scans', timeout=10000)

        # Verify New Controls in Left Panel
        # "Start Camera" should be visible and have text "Start Camera"
        expect(page.get_by_role("button", name="Start Camera")).to_be_visible()

        # Verify Undo Button Label
        expect(page.get_by_role("button", name="Undo")).to_be_visible()

        # Verify Recent Scans list has items (from our injected scans_temp.json)
        # Check for card name
        expect(page.get_by_text("Blue-Eyes White Dragon")).to_be_visible()

        # Take Screenshot
        page.screenshot(path="verification/verification_scan_layout_fix.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    run()
