from playwright.sync_api import sync_playwright, expect
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Wait for server to start
    max_retries = 10
    for i in range(max_retries):
        try:
            page.goto("http://localhost:8080")
            break
        except:
            if i == max_retries - 1:
                raise
            time.sleep(2)

    # Open Settings Drawer
    # The drawer toggle is in the header, usually a menu icon
    # Or the drawer is open by default on desktop?
    # Based on layout code: ui.left_drawer(value=True).classes('bg-dark text-white')
    # It might be open.

    # Look for the "Configuration" button in the drawer
    # It has text 'Configuration' and icon 'settings'
    # It might be inside a button component.

    # Wait for hydration
    page.wait_for_timeout(2000)

    # Click Configuration
    config_btn = page.get_by_text("Configuration")
    config_btn.click()

    # Wait for dialog to open
    # Dialog content: "Settings" label. Use the one in the dialog (class text-h6)
    expect(page.locator(".q-dialog .text-h6", has_text="Settings")).to_be_visible()

    # Check for "Generate Sample Collection" button
    gen_btn = page.get_by_text("Generate Sample Collection")
    expect(gen_btn).to_be_visible()

    # Take screenshot of the settings dialog
    os.makedirs("verification", exist_ok=True)
    page.screenshot(path="verification/settings_dialog_with_generate_button.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
