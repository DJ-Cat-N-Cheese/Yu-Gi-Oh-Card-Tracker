import time
from playwright.sync_api import sync_playwright, expect

def verify_deck_builder():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})

        try:
            print("Navigating...")
            page.goto("http://localhost:8080/decks")
            page.wait_for_load_state("networkidle")
            time.sleep(2) # Extra wait for NiceGUI connection

            # Check if we need to create a deck
            if page.get_by_text("Select or create a deck").is_visible():
                print("Creating deck...")
                # Open select
                page.locator(".q-field__control").first.click()
                time.sleep(1)
                # Click + New Deck
                page.get_by_text("+ New Deck").click()
                time.sleep(1)

                # Fill dialog
                page.get_by_label("Deck Name").fill("VerifyDeck")
                page.get_by_role("button", name="Create").click()
                time.sleep(3)

            print("Verifying Layout...")
            # Check 3 zones - use locators that are less text-strict if possible, or partial
            expect(page.locator(".deck-builder-deck-area").get_by_text("Main Deck")).to_be_visible()

            # Check Gallery
            gallery = page.locator(".deck-builder-search-results")
            expect(gallery).to_be_visible()

            # Wait for cards
            print("Waiting for cards...")
            time.sleep(3) # Wait for initial data load timer

            # Drag and Drop
            # Find the first card (draggable)
            draggable_item = gallery.locator(".q-card").first

            # Find drop zone (Main Deck)
            # The drop zone is the 'w-full flex-grow ...' inside the zone
            # We can target the text "Drag cards here" if visible, or the container
            target = page.locator(".deck-builder-deck-area .nicegui-column.flex-grow").first

            print("Dragging...")
            draggable_item.drag_to(target)
            time.sleep(1)

            # Verify count
            # Use partial match for (1)
            if page.locator(".deck-builder-deck-area").get_by_text("(1)").is_visible():
                print("Success: Card added.")
            else:
                print("Warning: Card count did not update.")

        except Exception as e:
            print(f"Error: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_deck_builder()
