from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to /scan...")
        page.goto("http://localhost:8080/scan")

        # Wait for "Recent Scans" header (indicates right panel loaded)
        try:
            page.wait_for_selector("text=Recent Scans", timeout=10000)
            print("Found 'Recent Scans' header.")
        except:
            print("Timeout waiting for 'Recent Scans' header. Dumping html.")
            with open("verification/debug_scan.html", "w") as f:
                f.write(page.content())

        # Wait a bit for layout
        time.sleep(2)

        page.screenshot(path="verification/scan_ui_refactor.png")
        print("Screenshot saved to verification/scan_ui_refactor.png")
        browser.close()

if __name__ == "__main__":
    run()
