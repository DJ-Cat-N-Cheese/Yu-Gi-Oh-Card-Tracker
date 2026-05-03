import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service

async def test():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    parsed_bls = {
        'card_info': {
            'title': 'Black Luster Soldier - Envoy of the Beginning',
            'number': 'IOC-EN025',
            'printed_in': 'Invasion of Chaos: 25th Anniversary Edition',
            'rarity': 'Secret Rare',
            'url': 'https://www.cardmarket.com/en/YuGiOh/Products/Singles/Invasion-of-Chaos-25th-Anniversary-Edition/Black-Luster-Soldier-Envoy-of-the-Beginning'
        }
    }

    # Run resolution
    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed_bls, ygo)
    print('BLS Resolve Variant ID:', var_id)
    print('Len cands:', len(cands))

    # Try another scenario! What if the API card was not found?
    # the user said "Black Luster Soldier - Envoy of the Beginning" for IOC-EN025
    # Wait, when parsing directly from the URL title (in test_parse_bls), the title is "Black Luster Soldier - Envoy of the Beginning - Invasion of Chaos: 25th Anniversary Edition"
    # Wait! the fallback name lookup does this:
    # clean_name = re.sub(r'\s*\([^\)]+(?:Rare|Common|Ultimate|Ghost|Prismatic)\)', '', title).strip()
    # clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()

    # If the Cardmarket title has the set name at the end separated by a dash:
    # "Black Luster Soldier - Envoy of the Beginning - Invasion of Chaos: 25th Anniversary Edition"
    # My manual script parsed the set code directly because my regex for `_infer_target_set_code` handled it!
    # Let me check what happens exactly when I do this.


asyncio.run(test())
