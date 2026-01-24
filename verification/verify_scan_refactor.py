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

        # Verify Top Header Elements
        # Target Collection selector (The label text)
        expect(page.locator(".q-field__label").filter(has_text="Target Collection")).to_be_visible()

        # Camera selector (The label text)
        expect(page.locator(".q-field__label").filter(has_text="Camera")).to_be_visible()

        # Defaults label
        expect(page.get_by_text("Defaults:", exact=True)).to_be_visible()

        # Commit button
        expect(page.get_by_role("button", name="Commit")).to_be_visible()

        # Verify Split Layout
        # Camera on left, Gallery on right.
        # "Capture & Scan" button on left
        expect(page.get_by_role("button", name="Capture & Scan")).to_be_visible()

        # Verify Recent Scans list has items (from our injected scans_temp.json)
        # Check for card name
        expect(page.get_by_text("Blue-Eyes White Dragon")).to_be_visible()

        # Check for Styling Elements
        # 1st Ed Badge? It's text "1st" with class text-orange-400
        # We can look for text "1st" inside a card
        expect(page.locator(".text-orange-400").filter(has_text="1st")).to_be_visible()

        # Take Screenshot
        page.screenshot(path="verification/verification_scan_refactor.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    run()
