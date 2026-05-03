import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service
from bs4 import BeautifulSoup
import re

async def main():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    # We can create fake parsed info that matches exactly what Cardmarket has
    html_text_dp = """
    <title>Dark Paladin (V.2 - Quarter Century Secret Rare) - Quarter Century Bonanza</title>
    <dl class="labeled">
        <dt>Number</dt><dd>RA03-EN004</dd>
        <dt>Printed in</dt><dd>Quarter Century Bonanza</dd>
        <dt>Rarity</dt><dd>Quarter Century Secret Rare</dd>
    </dl>
    """
    parsed_dp = pricing_service.parse_cardmarket_html(html_text_dp)
    print("Parsed DP:", parsed_dp)
    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed_dp, ygo)
    print("DP Resolve:", card_id, var_id, [(c.set_code, c.set_rarity) for c in cands])

    # Now let's try a case where RARITY might be slightly different.
    # What does the Yugioh API cache actually say about Dark Paladin from RA03?
    dp_card = ygo.search_by_name("Dark Paladin", language='en')
    for v in dp_card.card_sets:
        if 'RA03' in v.set_code:
            print(f"Dark Paladin Variant in DB: {v.set_code} - Rarity: '{v.set_rarity}'")

    bls_card = ygo.search_by_name("Black Luster Soldier - Envoy of the Beginning", language='en')
    for v in bls_card.card_sets:
        if 'IOC' in v.set_code:
            print(f"BLS Variant in DB: {v.set_code} - Rarity: '{v.set_rarity}'")

asyncio.run(main())
