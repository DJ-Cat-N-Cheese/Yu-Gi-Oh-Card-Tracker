import time
from playwright.sync_api import sync_playwright

def verify_bulk_add(page):
    page.goto("http://localhost:8080/bulk_add")
    time.sleep(3) # Wait for initial load

    # 1. Verify Header Controls
    # Look for the pagination label (e.g. "1/50")
    # It's a div or span with text like "1/"
    # Using regex to match digit/digit
    page.wait_for_selector('text=/^\d+\/\d+$/')

    # Look for Sort Select. It's a q-select.
    # We can check if "Name" (default) or "Newest" is visible in the select display.
    # Since I defaulted to Name in library and Newest in collection (Wait, collection default is Newest),
    # I should see "Name" in the library column and "Newest" in the collection column.

    # Library column is first. Collection is second.
    # Simplest is just check if the text "Name" and "Newest" appears in q-select elements.
    page.wait_for_selector('.q-field__native:has-text("Name")')
    page.wait_for_selector('.q-field__native:has-text("Newest")')

    # 2. Verify Card Content
    # Card name should be visible at the top of a card.
    # I'll take a screenshot to verify visually.

    # Take screenshot of the page
    page.screenshot(path="verification_bulk_add_ui.png")
    print("Screenshot saved to verification_bulk_add_ui.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_bulk_add(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification_failed.png")
        finally:
            browser.close()
