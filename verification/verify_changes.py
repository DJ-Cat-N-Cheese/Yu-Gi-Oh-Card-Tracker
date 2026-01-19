
from playwright.sync_api import sync_playwright, expect
import time

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Go to Bulk Add page
        print("Navigating to Bulk Add...")
        page.goto("http://localhost:8080/bulk_add")
        page.wait_for_selector('text="Bulk Add"')

        # 2. Open Structure Deck Dialog
        print("Opening Structure Deck Dialog...")
        page.get_by_role("button", name="Add Structure Deck").click()

        # Wait for dialog to open
        page.wait_for_selector('text="Select Structure Deck"')

        # Take screenshot of the dialog
        print("Taking screenshot...")
        page.screenshot(path="verification/structure_deck_dialog.png")

        # 3. Verify Tooltip Delay (by inspecting HTML if possible)
        # We need to find a card in the library
        # The library loads async.
        print("Checking library cards...")
        # Wait for at least one card
        try:
            page.wait_for_selector("#library-list .q-card", timeout=5000)

            # The tooltip is inside the card structure.
            # In the code:
            # with ui.card()...:
            #    ...
            #    self._setup_card_tooltip(...)
            #
            # _setup_card_tooltip does:
            # with ui.tooltip()...props('... delay=5000'):

            # In Quasar, q-tooltip is rendered. It might have the attribute.
            # We can try to select it.

            # Use evaluate to find if any element has delay="5000" or similar
            # Note: Quasar props might not be DOM attributes.
            # But let's dump the outerHTML of a tooltip to see.

            # Select the first tooltip element if found.
            # Note: q-tooltip is often display:none or not in DOM until hovered?
            # Actually, ui.tooltip() puts it in DOM.

            # Let's try to find it.
            # The tooltip is a child of the card (or the element it attaches to).

            # Let's just screenshot the library too.
            page.screenshot(path="verification/library_view.png")

        except Exception as e:
            print(f"Could not find library cards: {e}")

        browser.close()

if __name__ == "__main__":
    run_verification()
