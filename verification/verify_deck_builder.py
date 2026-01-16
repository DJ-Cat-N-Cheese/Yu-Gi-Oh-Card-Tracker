from playwright.sync_api import Page, expect, sync_playwright
import time
import uuid

def verify_deck_builder(page: Page):
    print("Navigating to Deck Builder...")
    page.goto("http://localhost:8080/decks")
    page.wait_for_load_state("networkidle")

    # Wait for initial data load
    expect(page.locator(".text-h5", has_text="Deck Builder")).to_be_visible(timeout=60000)

    print("Creating New Deck...")
    time.sleep(1)

    deck_select = page.locator(".q-field", has_text="Current Deck").first
    deck_select.click(force=True)

    page.locator(".q-item", has_text="+ New Deck").first.click()

    expect(page.get_by_text("Create New Deck")).to_be_visible()

    deck_name = f"Verif_{uuid.uuid4().hex[:4]}"
    page.get_by_label("Deck Name").fill(deck_name)
    page.get_by_role("button", name="Create").click()

    expect(page.get_by_text(deck_name)).to_be_visible()

    print("Searching for cards...")
    page.get_by_placeholder("Search cards...").fill("Dragon")
    time.sleep(2)

    # Use the new specific class for search results
    search_results = page.locator(".deck-builder-search-results")

    # Verify search results are present
    expect(search_results).to_be_visible()

    # Find cards inside the search results area
    cards = search_results.locator('.q-card')
    count = cards.count()
    print(f"Found {count} cards in search results.")

    if count == 0:
        print("No cards found in search results. Check API or search logic.")
        page.screenshot(path="verification/deck_builder_empty_search.png")
        # Fail explicitly
        raise Exception("No cards found in search results")

    first_card = cards.first
    print("Clicking first card to open dialog...")
    # Click on the image inside the card to ensure we hit the clickable area
    # The card itself has the click listener, but clicking the image is safe.
    first_card.click()

    print("Waiting for Add to Deck dialog...")
    # Use a more specific locator if possible, or wait longer
    expect(page.get_by_text("Add to Deck")).to_be_visible(timeout=5000)

    print("Adding card to Main Deck...")
    page.get_by_role("button", name="Add to Main").click()

    expect(page.get_by_text("Add to Deck")).not_to_be_visible()

    # Verify card in Main Deck
    # Check the Main Deck header updates count
    # It might take a moment
    time.sleep(1)

    deck_area = page.locator(".deck-builder-deck-area")
    expect(deck_area.get_by_text("Main Deck (1)")).to_be_visible()

    print("Taking success screenshot...")
    page.screenshot(path="verification/deck_builder_success.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_deck_builder(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/deck_builder_error.png")
        finally:
            browser.close()
