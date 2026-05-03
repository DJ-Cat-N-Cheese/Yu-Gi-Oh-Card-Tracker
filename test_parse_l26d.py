import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service

async def test():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    # IF the target_set_code is L26D-ENM10, api_card becomes Ame no Habakiri no Mitsurugi.
    parsed = {
        'card_info': {
            'title': 'Ame no Habakiri no Mitsurugi',
            'number': 'L26D-ENM10',
            'printed_in': 'Legendary Decks',
            'rarity': 'Common' # Cardmarket says 'Common'
        }
    }

    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed, ygo)
    print("Card ID:", card_id)
    print("Variant ID:", var_id)
    print("Len cands:", len(cands))

    # If the user says it literally says "No variants found in database. Item will be skipped."
    # then `cands` MUST BE EMPTY.
    # Why would `cands` be empty?

    # If `cands` is empty, then `api_card` is None!
    # If `api_card` is None, then BOTH Primary Lookup and Name Fallback Lookup FAILS.

    # Let me check my patch again. Maybe my patch caused it to be empty? No, the user said it happened BEFORE my patch.

asyncio.run(test())
