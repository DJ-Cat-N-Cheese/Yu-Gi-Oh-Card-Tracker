from bs4 import BeautifulSoup
import re
from src.services.pricing_service import pricing_service

html = """
<title>Dark Paladin (V.2 - Quarter Century Secret Rare) - Quarter Century Bonanza</title>
"""
parsed = pricing_service.parse_cardmarket_html(html)
print(parsed['card_info'])
