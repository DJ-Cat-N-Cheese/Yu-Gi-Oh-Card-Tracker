import asyncio
from src.services.pricing_service import pricing_service

async def test():
    url = "https://www.cardmarket.com/en/YuGiOh/Products/Singles/Age-of-Overlord/Crystal-God-Tistina"
    html = await pricing_service.fetch_html_from_url(url)

    print("Length of HTML received:", len(html))
    print("HTML excerpt:", html[:500])

asyncio.run(test())
