from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})

        # 1. Navigate to Home
        print("Navigating...")
        page.goto("http://localhost:8080")

        # 2. Navigate to Scan Page via Sidebar
        try:
            print("Clicking 'SCAN CARDS'...")
            page.get_by_text("SCAN CARDS").click()
            # Wait for Scan Page title or tabs
            page.wait_for_selector('text="Live Scan"', timeout=10000)
            print("Reached Scan Page")
        except Exception as e:
            print(f"Navigation failed: {e}")
            page.screenshot(path="nav_fail.png")
            return

        # 3. Check for Condition Dropdown
        try:
            # "Default Condition" is the label of the select
            # Note: Quasar select labels might be in a span or div
            # Expect text "Default Condition" to be visible
            expect(page.get_by_text("Default Condition")).to_be_visible()
            print("Found Default Condition label")

            # Check Value "Near Mint"
            expect(page.get_by_text("Near Mint")).to_be_visible()
            print("Found Near Mint value")

        except Exception as e:
            print(f"Failed to find elements: {e}")

        # 4. Screenshot
        page.screenshot(path="verification_scan_page_final.png")
        print("Screenshot taken")

        browser.close()

if __name__ == "__main__":
    run()
