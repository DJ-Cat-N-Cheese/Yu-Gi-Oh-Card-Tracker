import time
from playwright.sync_api import sync_playwright, expect

def verify_deck_builder():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Use a common desktop resolution
        page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            print("Navigating...")
            page.goto("http://localhost:8080/decks")
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # Check Gallery
            gallery = page.locator(".deck-builder-search-results")
            expect(gallery).to_be_visible()

            box = gallery.bounding_box()
            print(f"Gallery Box: {box}")

            deck_area = page.locator(".deck-builder-deck-area")
            deck_box = deck_area.bounding_box()
            print(f"Deck Area Box: {deck_box}")

            if box['width'] < 10:
                print("FAILURE: Gallery width is almost zero!")
            else:
                print("Gallery seems to have width.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_deck_builder()
