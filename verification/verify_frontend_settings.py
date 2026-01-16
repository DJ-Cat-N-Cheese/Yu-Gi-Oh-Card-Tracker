from playwright.sync_api import Page, expect, sync_playwright
import time

def verify_settings_menu(page: Page):
    print("Navigating to home...")
    page.goto("http://localhost:8080")

    # Wait for page load
    page.wait_for_load_state("networkidle")

    # Open settings
    # The button is likely in the sidebar, labeled "Configuration" or icon "settings"
    print("Opening settings...")

    # Sometimes sidebar is toggleable. Assuming it's open by default on desktop size.
    # Look for button "Configuration"
    settings_btn = page.get_by_role("button", name="Configuration")
    if not settings_btn.is_visible():
        # Try to open sidebar if closed? Or maybe it's just loading.
        # Let's try to find the menu button to toggle sidebar if needed, but let's assume it's visible first.
        print("Settings button not visible, checking for menu button...")
        pass

    settings_btn.click()

    # Wait for dialog
    print("Waiting for dialog...")
    dialog = page.locator(".q-dialog") # NiceGUI uses Quasar, dialogs are q-dialog
    expect(dialog).to_be_visible()

    # Check for buttons
    print("Verifying buttons...")

    # "Fix Legacy Set Codes" should NOT be there
    fix_btn = page.get_by_role("button", name="Fix Legacy Set Codes")
    expect(fix_btn).not_to_be_visible()
    print("Confirmed: 'Fix Legacy Set Codes' button is missing.")

    # "Generate Sample Collection" SHOULD be there
    gen_btn = page.get_by_role("button", name="Generate Sample Collection")
    expect(gen_btn).to_be_visible()
    print("Confirmed: 'Generate Sample Collection' button is present.")

    # Take screenshot
    print("Taking screenshot...")
    # Wait a bit for animations
    time.sleep(1)
    page.screenshot(path="/app/verification/settings_dialog.png")
    print("Screenshot saved.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a large viewport to ensure sidebar is likely open
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        try:
            verify_settings_menu(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="/app/verification/error_screenshot.png")
        finally:
            browser.close()
