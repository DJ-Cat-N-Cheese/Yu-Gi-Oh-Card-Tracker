import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service

async def test():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    # Let's test precisely what happens if title is strictly "Dark Paladin (V.2 - Quarter Century Secret Rare)"
    # but the number parsed is "RA03-EN004".
    # Wait, the user said NO RESULTS for Dark Paladin!
    # My script printed "Card ID: 78868119" (which is Deep Sea Diva).
    # If it resolves to Deep Sea Diva, then the UI won't show "No variants found in database. Item will be skipped." for Dark Paladin, it would just show Deep Sea Diva in the parsed_results tab instead of the ambiguous tab.
    # UNLESS `target_set_code` parsing fails or `resolve_card_variant` returns `None, None, []`!

    # Why would it return `None, None, []`?
    # Because api_card becomes None!
    # Let's run a test where target_set_code is EMPTY or mismatched.

    parsed_dp = {
        'card_info': {
            'title': 'Dark Paladin (V.2 - Quarter Century Secret Rare) - Quarter Century Bonanza',
            'number': 'RA03-EN004', # What if the number is different or missing?
            'printed_in': 'Quarter Century Bonanza',
            'rarity': 'Quarter Century Secret Rare',
            'url': 'https://www.cardmarket.com/en/YuGiOh/Products/Singles/Quarter-Century-Bonanza/Dark-Paladin-V2-Quarter-Century-Secret-Rare'
        }
    }

    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed_dp, ygo)
    print("Test 1:")
    print("card_id:", card_id, "var_id:", var_id, "len cands:", len(cands))

    # What if the title parsing is EXACTLY what Cardmarket serves from URL fallback?
    # Let's manually run the exact sequence in resolve_card_variant

    title = 'Dark Paladin (V.2 - Quarter Century Secret Rare) - Quarter Century Bonanza'

    import re
    clean_name = re.sub(r'\s*\(V\.\d+(?:\s*-\s*[^\)]+)?\)', '', title)
    clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()
    print("Clean name 1:", clean_name)
    # The output of clean_name here is "Dark Paladin - Quarter Century Bonanza"
    # Because of the dash at the end!

    # And then we search by name for "Dark Paladin - Quarter Century Bonanza", which FAILS!
    # Then fallback clean_name:
    clean_name2 = re.sub(r'\s*\([^\)]+(?:Rare|Common|Ultimate|Ghost|Prismatic)\)', '', title).strip()
    clean_name2 = re.split(r'\s*-\s*YGO Singles', clean_name2)[0].strip()
    print("Clean name 2:", clean_name2)
    # The output here is still "Dark Paladin - Quarter Century Bonanza"

    # And we search for "Dark Paladin - Quarter Century Bonanza" which FAILS!
    # If `target_set_code` wasn't found (e.g. number wasn't extracted from the page), then api_card remains None!

asyncio.run(test())
