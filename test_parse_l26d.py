import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service

async def test():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    html = '''
    <html>
        <title>Ame no Habakiri no Mitsurugi - 2024 Tin: Dueling Mirrors</title>
        <dl class="labeled">
            <dt>Number</dt><dd>L26D-ENM10</dd>
            <dt>Printed in</dt><dd>2024 Tin: Dueling Mirrors</dd>
            <dt>Rarity</dt><dd>Common</dd>
        </dl>
    </html>
    '''
    parsed = pricing_service.parse_cardmarket_html(html)
    card_id, var_id, cands = pricing_service.resolve_card_variant(parsed, ygo)
    print('With number:')
    print(card_id, var_id, len(cands))

    html2 = '''
    <html>
        <title>Ame no Habakiri no Mitsurugi - 2024 Tin: Dueling Mirrors</title>
    </html>
    '''
    parsed2 = pricing_service.parse_cardmarket_html(html2)
    card_id2, var_id2, cands2 = pricing_service.resolve_card_variant(parsed2, ygo)
    print('Without number:')
    print(card_id2, var_id2, len(cands2))

asyncio.run(test())
