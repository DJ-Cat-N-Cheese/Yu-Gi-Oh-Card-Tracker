import unittest
from src.services.pricing_service import pricing_service

class TestCardmarketHtmlRepro(unittest.TestCase):
    def test_repro_parsing_logic(self):
        html_text = """
        <dl class="labeled">
          <dt>Rarity</dt>
          <dd>
            <span class="icon" title="Quarter Century Secret Rare">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 22h20L12 2zm0 3.5l7 14.5H5l7-14.5z"/></svg>
            </span>
          </dd>
        </dl>
        """
        res = pricing_service.parse_cardmarket_html(html_text)
        self.assertEqual(res['card_info']['rarity'], 'Quarter Century Secret Rare')

if __name__ == '__main__':
    unittest.main()
