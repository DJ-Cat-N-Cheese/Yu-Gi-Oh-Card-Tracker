import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service
from src.services.yugipedia_service import YugipediaService

async def main():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    # In my test script, DP returned 1 cand and was resolved.
    # Let me check what set_code DP actually is!
    # Wait! Dark Paladin RA03 is RA03-EN126 in the DB, but RA03-EN004 in Cardmarket!
    # Cardmarket says "RA03-EN004", DB says "RA03-EN126".
    print("Test DP with Cardmarket set_code:")
    parsed_dp2 = {
        'card_info': {
            'title': 'Dark Paladin (V.2 - Quarter Century Secret Rare)',
            'number': 'RA03-EN004',
            'printed_in': 'Quarter Century Bonanza',
            'rarity': 'Quarter Century Secret Rare',
            'url': 'https://www.cardmarket.com/en/YuGiOh/Products/Singles/Quarter-Century-Bonanza/Dark-Paladin-V2-Quarter-Century-Secret-Rare'
        }
    }

    c_id, v_id, cands = pricing_service.resolve_card_variant(parsed_dp2, ygo)
    print("DP Resolve:", c_id, v_id, [(c.set_code, c.set_rarity) for c in cands])

asyncio.run(main())
