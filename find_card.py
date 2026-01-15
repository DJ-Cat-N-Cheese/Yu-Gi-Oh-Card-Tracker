import asyncio
import os
import sys

sys.path.append(os.getcwd())
from src.services.ygo_api import ygo_service

async def main():
    print("Searching...")
    try:
        cards = await ygo_service.load_card_database("en")
    except:
        return

    dm = next((c for c in cards if c.name == "Dark Magician"), None)
    if dm:
        print(f"Found: {dm.name}")
        if dm.card_sets:
            print(f"Set 0: {dm.card_sets[0].set_code} - {dm.card_sets[0].set_rarity}")
            print(f"Set 1: {dm.card_sets[1].set_code} - {dm.card_sets[1].set_rarity}")
    else:
        print("Dark Magician not found")

if __name__ == "__main__":
    asyncio.run(main())
