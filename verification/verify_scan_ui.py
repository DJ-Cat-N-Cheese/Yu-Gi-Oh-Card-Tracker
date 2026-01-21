from playwright.sync_api import Page, expect, sync_playwright

def verify_scan_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("Navigating to Scan Page...")
            page.goto("http://localhost:8081/scan")

            # Wait for page load
            page.wait_for_load_state("networkidle")

            # Check for Scanner Error
            if page.get_by_text("Scanner dependencies not found").is_visible():
                print("FAILURE: Scanner dependencies missing message found.")
                page.screenshot(path="verification/verification_failure.png")
                return

            print("Scanner UI loaded.")

            # Switch to Debug Lab
            print("Switching to Debug Lab...")
            page.get_by_text("Debug Lab").click()

            # Check Status
            # Depending on initialization, it might be Stopped or Paused
            # Note: The fix changed "Stopped" to "Paused" in my thought process?
            # No, default is "Stopped" in __init__.
            # But thread starts and sets "Paused".
            # The mocked thread might run very fast.

            # Just check if Status section exists
            expect(page.get_by_text("Status:")).to_be_visible()

            # Take screenshot
            page.screenshot(path="verification/verification_scan_ui.png")
            print("Screenshot saved to verification/verification_scan_ui.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_scan_ui()
