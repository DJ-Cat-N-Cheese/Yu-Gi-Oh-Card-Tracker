import time
from playwright.sync_api import sync_playwright

def debug_dom_structure():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        print("Navigating...")
        page.goto("http://localhost:8080/decks")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Target the left column
        left_col = page.locator(".deck-builder-search-results")

        # Dump the HTML structure of the left column (truncated)
        html = left_col.inner_html()
        print("Left Col Inner HTML (first 1000 chars):")
        print(html[:1000])

        # Check for card visibility specifically
        card = left_col.locator(".q-card").first
        if card.count() > 0:
            print("First Card found.")
            box = card.bounding_box()
            print(f"Card Box: {box}")
            vis = card.is_visible()
            print(f"Card Visible (Playwright): {vis}")

            # Check computed styles
            bg = card.evaluate("el => window.getComputedStyle(el).backgroundColor")
            print(f"Card BG Color: {bg}")
            opacity = card.evaluate("el => window.getComputedStyle(el).opacity")
            print(f"Card Opacity: {opacity}")
            display = card.evaluate("el => window.getComputedStyle(el).display")
            print(f"Card Display: {display}")

            # Check parent of the card
            parent = card.locator("..")
            print(f"Card Parent Class: {parent.get_attribute('class')}")
            pbox = parent.bounding_box()
            print(f"Card Parent Box: {pbox}")

        else:
            print("No cards found in Left Col.")

        browser.close()

if __name__ == "__main__":
    debug_dom_structure()
