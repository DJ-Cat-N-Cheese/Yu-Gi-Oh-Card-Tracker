from playwright.sync_api import sync_playwright, expect
import time
import os

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8080")

        # 1. Collection Page
        try:
            page.get_by_text("Collection").first.click()
        except:
            pass

        time.sleep(2)

        # Switch to Collectors View
        # Button with text "Collectors"
        page.get_by_role("button", name="Collectors").click()
        time.sleep(1)

        # Select test_collection if not selected
        # (Assuming it's selected as I only have one? Or defaults to first?
        # seed_verification.py created test_collection.json.
        # CollectionPage loads files[0]. If there are others, I might need to switch.
        # But let's assume it works or I'd see empty.)

        page.screenshot(path="verification_screenshots/collection_page.png")
        print("Captured collection_page.png")

        # 2. Bulk Add Page
        try:
            page.get_by_text("Bulk Add").first.click()
        except:
            print("Could not find Bulk Add link")

        time.sleep(2)
        # In Bulk Add, we need to ensure "test_collection" is selected.
        # It defaults to files[0].
        # And we need to ensure the collection list is populated.

        page.screenshot(path="verification_screenshots/bulk_add_page.png")
        print("Captured bulk_add_page.png")

        browser.close()

if __name__ == "__main__":
    verify_frontend()
