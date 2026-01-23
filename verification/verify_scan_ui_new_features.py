from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8080/scan")

    # Wait for page load
    page.wait_for_selector('text=Live Scan')

    # Verify Default Condition Dropdown
    # I added a ui.select with label "Default Condition"
    # We look for the text "Default Condition"
    expect(page.get_by_text("Default Condition")).to_be_visible()

    # Verify "Add All" button
    expect(page.get_by_role("button", name="Add All")).to_be_visible()

    # Take screenshot
    page.screenshot(path="verification/scan_ui_features.png")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
