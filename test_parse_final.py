import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service

async def test():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    parsed = {
        'card_info': {
            'title': 'Dark Paladin (V.2 - Quarter Century Secret Rare) - Quarter Century Bonanza',
            'number': 'RA03-EN004',
            'printed_in': 'Quarter Century Bonanza',
            'rarity': 'Quarter Century Secret Rare',
            'url': 'https://www.cardmarket.com/en/YuGiOh/Products/Singles/Quarter-Century-Bonanza/Dark-Paladin-V2-Quarter-Century-Secret-Rare'
        }
    }

    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed, ygo)
    print("FINAL DP Resolve:")
    print("ID:", card_id, "Variant:", var_id, "Len:", len(cands))

    parsed_bls = {
        'card_info': {
            'title': 'Black Luster Soldier - Envoy of the Beginning - Invasion of Chaos: 25th Anniversary Edition',
            'number': 'IOC-EN025',
            'printed_in': 'Invasion of Chaos: 25th Anniversary Edition',
            'rarity': 'Secret Rare',
            'url': 'https://www.cardmarket.com/en/YuGiOh/Products/Singles/Invasion-of-Chaos-25th-Anniversary-Edition/Black-Luster-Soldier-Envoy-of-the-Beginning'
        }
    }
    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed_bls, ygo)
    print("FINAL BLS Resolve:")
    print("ID:", card_id, "Variant:", var_id, "Len:", len(cands))

    parsed_l26d = {
        'card_info': {
            'title': 'Ame no Habakiri no Mitsurugi',
            'number': 'L26D-EN010'
        }
    }
    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed_l26d, ygo)
    print("FINAL L26D Resolve:")
    print("ID:", card_id, "Variant:", var_id, "Len:", len(cands))

asyncio.run(test())
