import time
from playwright.sync_api import sync_playwright, expect

def verify_layout_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            print("Navigating...")
            page.goto("http://localhost:8080/decks")
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # Check Gallery and Deck Area visibility
            gallery = page.locator(".deck-builder-search-results")
            deck_area = page.locator(".deck-builder-deck-area")

            expect(gallery).to_be_visible()
            expect(deck_area).to_be_visible()

            # Take screenshot
            screenshot_path = "verification/deck_builder_layout.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_layout_screenshot()
