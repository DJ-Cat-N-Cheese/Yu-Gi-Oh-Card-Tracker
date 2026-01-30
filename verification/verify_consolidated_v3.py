import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Ensure data directories exist
os.makedirs('data/images', exist_ok=True)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("Navigating to DB Editor...")
            # The route defined in main.py is /db_editor
            await page.goto("http://localhost:8080/db_editor")

            # Wait for the page to load (look for the header)
            await page.wait_for_selector('text=Card Database Editor', timeout=10000)

            print("Switching to Consolidated View...")
            # The button text is "Consolidated" inside a button group
            await page.click('button:has-text("Consolidated")', timeout=5000)
            await asyncio.sleep(2) # Wait for view switch and data reload

            print("Clicking on a card to open details...")
            # Click the first card card-element
            # In db_editor.py: ui.card()...on('click', ...)
            # We can target the first .collection-card
            await page.click('.collection-card', timeout=5000)

            print("Waiting for Consolidated View modal...")
            # Title is "Consolidated View: {Card Name}"
            await page.wait_for_selector('text=Consolidated View:', timeout=10000)

            print("Checking for Select All checkbox...")
            # Select All checkbox is in the header.
            # It should be the first checkbox in the dialog.
            # We wait a bit for the variants to render
            await asyncio.sleep(1)

            checkboxes = await page.query_selector_all('.q-checkbox')
            if not checkboxes:
                print("Error: No checkboxes found.")
                return

            select_all = checkboxes[0]
            print("Clicking Select All...")
            await select_all.click()
            await asyncio.sleep(0.5)

            print("Taking screenshot...")
            await page.screenshot(path='verification/consolidated_view_v3.png')

            print("Verifying selection state...")
            # Check if other checkboxes are checked
            # This is tricky with Playwright and Quasar as the input might be hidden or the class changes.
            # We look for 'aria-checked="true"' or similar on the role='checkbox' div

            checked_count = 0
            # Re-query checkboxes to get current state
            checkboxes = await page.query_selector_all('.q-checkbox')

            for i, cb in enumerate(checkboxes):
                # checking attribute aria-checked
                is_checked = await cb.get_attribute('aria-checked')
                # print(f"Checkbox {i}: aria-checked={is_checked}")
                if is_checked == 'true':
                    checked_count += 1

            print(f"Total checked: {checked_count} / {len(checkboxes)}")

            # Expect all to be checked (or all but none if logic failed)
            # There should be at least one variant plus the select all header, so > 1
            if checked_count > 1:
                print("SUCCESS: Multiple checkboxes checked.")
            else:
                print("FAILURE: Select All did not check other boxes.")

        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path='verification/error_v3.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
