import time
from playwright.sync_api import sync_playwright, expect

def verify_cards_exist():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            print("Navigating...")
            page.goto("http://localhost:8080/decks")
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # Check Gallery Container
            gallery = page.locator(".deck-builder-search-results")
            expect(gallery).to_be_visible()

            # Count cards
            cards = gallery.locator(".q-card")
            count = cards.count()
            print(f"Found {count} cards in gallery.")

            if count == 0:
                print("FAILURE: No cards found in gallery.")
                # Print inner HTML of the gallery to debug
                print("Gallery Inner HTML:")
                print(gallery.inner_html())
            else:
                print("Success: Cards are present.")
                # Check visibility of first card
                first_card = cards.first
                if first_card.is_visible():
                    print("First card is visible.")
                else:
                    print("First card is NOT visible.")
                    print(f"First card box: {first_card.bounding_box()}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_cards_exist()
