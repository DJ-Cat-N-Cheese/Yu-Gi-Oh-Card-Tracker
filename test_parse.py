import asyncio
from src.services.ygo_api import YugiohService
from src.services.pricing_service import pricing_service

async def main():
    ygo = YugiohService()
    await ygo.load_card_database('en')

    html1 = await pricing_service.fetch_html_from_url('https://www.cardmarket.com/en/YuGiOh/Products/Singles/Quarter-Century-Bonanza/Dark-Paladin-V2-Quarter-Century-Secret-Rare')
    parsed_info_1 = pricing_service.parse_cardmarket_html(html1)
    # The cloudflare challenge will block the request.
    # Let me mock the parsed_info dictionary but what if my parsing is different?
    print(parsed_info_1)

asyncio.run(main())
