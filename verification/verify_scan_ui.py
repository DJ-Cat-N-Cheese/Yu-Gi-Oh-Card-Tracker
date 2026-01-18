from playwright.sync_api import sync_playwright, expect

def verify_scan_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to home
        page.goto("http://localhost:8080")

        # Check title
        expect(page).to_have_title("OpenYuGi")

        # Click Scan Cards in sidebar
        # Sidebar might be hidden?
        # The sidebar is `left_drawer(value=True)` so it should be visible.
        # It has `nav_button('Scan Cards', ...)`

        page.get_by_text("Scan Cards").click()

        # Verify URL
        expect(page).to_have_url("http://localhost:8080/scan")

        # Verify Headers
        expect(page.get_by_text("Card Scanner")).to_be_visible()
        expect(page.get_by_text("Session Scanned Cards")).to_be_visible()

        # Verify Buttons
        expect(page.get_by_role("button", name="Start Camera")).to_be_visible()
        expect(page.get_by_role("button", name="Stop Camera")).to_be_visible()

        # Take screenshot
        page.screenshot(path="verification/scan_page.png")

        browser.close()

if __name__ == "__main__":
    verify_scan_page()
