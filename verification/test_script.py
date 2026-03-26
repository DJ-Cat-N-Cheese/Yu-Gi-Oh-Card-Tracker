from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate
        page.goto('http://localhost:8080')
        page.wait_for_timeout(2000)

        page.screenshot(path="verification/clean_db_dialog1.png")

        # Click Config
        page.get_by_text("Configuration").click()
        page.wait_for_timeout(1000)

        page.screenshot(path="verification/clean_db_dialog2.png")

        # Click Clean Database
        page.get_by_text("Clean Database Entries").click()
        page.wait_for_timeout(1000)

        # Make sure the dialog opens
        page.screenshot(path="verification/clean_db_dialog3.png")

        # Find Scan button in dialog
        page.get_by_text("Scan", exact=True).click()
        page.wait_for_timeout(2000)

        # Make sure the dialog opens
        page.screenshot(path="verification/clean_db_dialog4.png")

        print("Success!")
        browser.close()

if __name__ == "__main__":
    verify()
