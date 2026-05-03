import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service
import re

async def test():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    parsed_bls = {
        'card_info': {
            'title': 'Black Luster Soldier - Envoy of the Beginning - Invasion of Chaos: 25th Anniversary Edition',
            'number': 'IOC-EN025',
            'printed_in': 'Invasion of Chaos: 25th Anniversary Edition',
            'rarity': 'Secret Rare',
            'url': 'https://www.cardmarket.com/en/YuGiOh/Products/Singles/Invasion-of-Chaos-25th-Anniversary-Edition/Black-Luster-Soldier-Envoy-of-the-Beginning'
        }
    }

    parsed_info = parsed_bls
    title = parsed_info['card_info'].get('title', '')
    rarity = parsed_info['card_info'].get('rarity', '')
    target_set_code = pricing_service._infer_target_set_code(parsed_info, ygo)
    print('Target set code:', target_set_code)

    clean_name = re.sub(r'\s*\(V\.\d+(?:\s*-\s*[^\)]+)?\)', '', title)
    clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()
    print('Clean name:', clean_name)

    api_card = None

    if target_set_code and '-' in target_set_code:
        for c in ygo._cards_cache.get('en', []):
            for v in c.card_sets:
                if target_set_code.lower() == v.set_code.lower() or target_set_code.lower() in v.set_code.lower():
                    api_card = c
                    break
            if api_card:
                break

    print('API Card Name from Set Code:', api_card.name if api_card else 'None')

asyncio.run(test())
