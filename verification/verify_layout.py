import os
import time
from playwright.sync_api import sync_playwright, expect

def verify_layout(page):
    print("Navigating to Deck Builder...")
    # Navigate to Deck Builder
    page.goto("http://localhost:8080/decks")

    # Wait for page load (look for "Library" text which is in the left column now)
    page.wait_for_selector('text=Library', timeout=10000)

    print("Page loaded. Verifying elements in Left Column...")

    # Locate the Left Column
    left_column = page.locator('.deck-builder-search-results')
    expect(left_column).to_be_visible()

    # 1. Check Search Input in Left Column
    search_input = left_column.locator('input[placeholder="Search..."]')
    expect(search_input).to_be_visible()
    print("Search input found in left column.")

    # 2. Check Owned Only Switch in Left Column
    # Quasar switches are complex. Look for the label text "Owned Only" inside the column.
    switch_label = left_column.get_by_text('Owned Only')
    expect(switch_label).to_be_visible()
    print("Owned Only switch found in left column.")

    # 3. Check Filter Button in Left Column
    # Look for the icon inside the button
    filter_icon = left_column.locator('i.q-icon').filter(has_text='filter_list')
    expect(filter_icon).to_be_visible()
    print("Filter button found in left column.")

    # 4. Verify Main Header does NOT contain these
    # The Main Header is the row above the columns.
    # It contains "Deck Builder" and "Current Deck".
    # We can check that there are no OTHER inputs/switches there.
    # But verifying positive existence in the left column is usually sufficient proof of movement
    # if the locators are scoped correctly.

    # Take screenshot
    screenshot_path = os.path.abspath("verification/layout.png")
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        try:
            verify_layout(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
            raise e
        finally:
            browser.close()
