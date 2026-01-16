
import os
import sys
from playwright.sync_api import sync_playwright

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Set headless=False to see it
        page = browser.new_page()

        # 1. Open the page
        print("Opening page...")
        page.goto("http://localhost:8080/collection")

        # Wait for page to load (look for "Gallery")
        page.wait_for_selector('text="Gallery"')
        print("Page loaded.")

        # 3. Turn on "Owned" filter
        print("Toggling 'Owned' filter...")
        owned_toggle = page.locator('div.q-toggle__label:has-text("Owned")')
        owned_toggle.click()
        page.wait_for_timeout(1000)

        # 4. Search for "Dark Magician"
        print("Searching for 'Dark Magician'...")
        search_input = page.locator('input[type="text"]').first
        search_input.fill("Dark Magician")
        page.wait_for_timeout(2000)

        # 5. Verify "Dark Magician" card is visible in Consolidated view
        print("Verifying Consolidated view...")
        dm_card = page.locator('.q-card').filter(has_text="Dark Magician").first
        if dm_card.is_visible():
            print("SUCCESS: Found 'Dark Magician' in Consolidated view.")
        else:
            print("FAILURE: 'Dark Magician' not found in Consolidated view.")
            page.screenshot(path="verification/verification_consolidated_fail.png")

        # 6. Switch to "Collectors" view
        print("Switching to Collectors view...")
        page.get_by_role("button", name="COLLECTORS").click()

        # Wait for view switch
        page.wait_for_timeout(1000)

        # 7. Verify SDY-006 row
        print("Verifying SDY-006...")
        # Use .first to avoid strict mode violation if multiple variants match
        sdy_row = page.locator('text="SDY-006"').first
        if sdy_row.is_visible():
            print("SUCCESS: Found 'SDY-006' in Collectors view.")
        else:
            print("FAILURE: 'SDY-006' not found in Collectors view.")
            page.screenshot(path="verification/verification_collectors_fail.png")
            with open("verification/page_dump.html", "w") as f:
                f.write(page.content())

        browser.close()

if __name__ == "__main__":
    verify_frontend()
