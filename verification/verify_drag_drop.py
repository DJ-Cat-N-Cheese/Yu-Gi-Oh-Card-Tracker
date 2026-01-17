import asyncio
from playwright.async_api import async_playwright
import time

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

        print("Navigating to deck builder...")
        await page.goto("http://localhost:8080/deck_builder")

        print("Waiting for gallery to populate (timeout 30s)...")
        try:
            # Wait for any card content
            gallery_card = await page.wait_for_selector("#gallery-list .q-card", timeout=30000)
        except Exception as e:
            print(f"Timeout waiting for gallery card: {e}")
            return

        parent_div = await gallery_card.evaluate_handle("el => el.parentElement")
        card_id = await parent_div.get_attribute("data-id")
        print(f"Gallery card ID: {card_id}")

        main_deck = page.locator("#deck-main")

        src_box = await gallery_card.bounding_box()
        target_box = await main_deck.bounding_box()

        if not src_box or not target_box:
            print("Could not get bounding boxes.")
            return

        print("Performing drag and drop...")
        await page.mouse.move(src_box["x"] + src_box["width"] / 2, src_box["y"] + src_box["height"] / 2)
        await page.mouse.down()
        await page.mouse.move(target_box["x"] + target_box["width"] / 2, target_box["y"] + target_box["height"] / 2, steps=10)
        await page.mouse.up()

        print("Drag action performed.")

        time.sleep(3)

        deck_card_selector = f"#deck-main div[data-id='{card_id}']"
        deck_card = page.locator(deck_card_selector)

        if await deck_card.count() > 0:
            print("Card found in Main Deck.")

            await deck_card.first.hover()

            try:
                tooltip_img = page.locator(".q-tooltip img")
                await tooltip_img.wait_for(state="visible", timeout=5000)
                print("Tooltip detected.")
            except:
                print("Tooltip NOT detected or timed out.")
        else:
            print("Card NOT found in Main Deck after drag.")

        print("Clicking gallery card...")
        await gallery_card.click()

        try:
            dialog = page.locator(".q-dialog")
            await dialog.wait_for(state="visible", timeout=5000)
            print("Dialog opened successfully.")
        except:
            print("Dialog did NOT open.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
