import json
import logging
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp

logger = logging.getLogger(__name__)

class PricingService:
    def __init__(self):
        self.daily_pricing_file = "data/prices/daily_card_pricing.json"
        self.offers_pricing_file = "data/prices/cardmarket_offers_pricing.json"

        # Ensure data dir exists
        os.makedirs("data/prices", exist_ok=True)

        # Load existing data
        self.daily_pricing = self._load_json(self.daily_pricing_file)
        self.offers_pricing = self._load_json(self.offers_pricing_file)

    def _load_json(self, path: str) -> Dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
        return {}

    def _save_json(self, path: str, data: Dict):
        try:
            with open(path, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving {path}: {e}")

    async def fetch_html_from_url(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            # Setting common browser headers to avoid basic blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                logger.error(f"Failed to fetch url {url}: {e}")
                return ""

    def parse_cardmarket_html(self, html_text: str) -> Dict[str, Any]:
        """Parses Cardmarket HTML to extract prices, offers and card info."""
        data = {'prices': [], 'offers': [], 'card_info': {}}

        # 1. Prices from chart JS
        script_match = re.search(r'var myLineChart.*?new Chart\([^,]+,\{(.*?)\}\);', html_text, re.DOTALL)
        if script_match:
            chart_data_str = "{" + script_match.group(1) + "}"
            labels_match = re.search(r'"labels":\[(.*?)\]', chart_data_str)
            data_match = re.search(r'"data":\[(.*?)\]', chart_data_str)
            if labels_match and data_match:
                labels = [l.strip('"').strip() for l in labels_match.group(1).split(',')]
                # Filter out empty strings in data
                raw_data = data_match.group(1).split(',')
                prices = []
                for d in raw_data:
                    d_clean = d.strip()
                    if d_clean:
                        try:
                            prices.append(float(d_clean))
                        except ValueError:
                            prices.append(0.0)
                    else:
                        prices.append(0.0)

                # Only zip up to the length of the shortest list to be safe
                min_len = min(len(labels), len(prices))
                data['prices'] = list(zip(labels[:min_len], prices[:min_len]))

        # 2. Card info & Offers via BeautifulSoup
        soup = BeautifulSoup(html_text, 'html.parser')

        title_el = soup.select_one('title')
        if title_el:
            data['card_info']['title'] = title_el.text.strip()

        # Extract number, rarity, printed in from the definition list
        dt_els = soup.select('dl.labeled dt')
        dd_els = soup.select('dl.labeled dd')

        for dt, dd in zip(dt_els, dd_els):
            dt_text = dt.text.strip()
            dd_text = dd.text.strip()

            if dt_text == "Number":
                data['card_info']['number'] = dd_text
            elif dt_text == "Printed in":
                data['card_info']['printed_in'] = dd_text
            elif dt_text == "Rarity":
                # Rarity might be inside an svg title, or just text
                svg_el = dd.select_one('svg')
                if svg_el and svg_el.has_attr('data-bs-original-title'):
                    data['card_info']['rarity'] = svg_el['data-bs-original-title']
                elif svg_el and svg_el.has_attr('aria-label'):
                    data['card_info']['rarity'] = svg_el['aria-label']
                else:
                    data['card_info']['rarity'] = dd_text

        # Try to infer rarity from title if not found (e.g. "(V.1 - Secret Rare)")
        if 'rarity' not in data['card_info'] or not data['card_info']['rarity']:
            title = data['card_info'].get('title', '')
            rarity_match = re.search(r'\((?:V\.\d+\s*-\s*)?([^\)]+Rare|[^\)]+Ultra|[^\)]+Common|[^\)]+Ghost|[^\)]+Ultimate|[^\)]+Prismatic)\)', title, re.IGNORECASE)
            if rarity_match:
                data['card_info']['rarity'] = rarity_match.group(1).strip()

        # Extract Offers
        rows = soup.select('div.article-row')
        for row in rows:
            seller_el = row.select_one('.seller-name a')
            seller_name = seller_el.text.strip() if seller_el else ""

            loc_el = row.select_one('.seller-name .icon[aria-label^="Item location:"]')
            loc = loc_el['aria-label'].replace("Item location: ", "").strip() if loc_el else ""

            cond_el = row.select_one('.article-condition .badge')
            cond = cond_el.text.strip() if cond_el else ""

            first_ed_el = row.select_one('.st_SpecialIcon[aria-label="First Edition"]')
            first_ed = bool(first_ed_el)

            qty_el = row.select_one('.amount-container .item-count')
            qty = int(qty_el.text.strip()) if qty_el and qty_el.text.strip().isdigit() else 1

            comment_el = row.select_one('.product-comments span.text-truncate')
            comment = comment_el.text.strip() if comment_el else ""

            price_el = row.select_one('.price-container .color-primary')
            if not price_el:
                price_el = row.select_one('.mobile-offer-container .color-primary')

            price = 0.0
            if price_el:
                price_str = price_el.text.replace('€', '').replace(',', '.').strip()
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            if seller_name and price > 0:
                data['offers'].append({
                    'seller_name': seller_name,
                    'seller_location': loc,
                    'condition': cond,
                    'first_edition': first_ed,
                    'quantity': qty,
                    'comment': comment,
                    'price': price
                })

        return data

    def resolve_card_variant(self, parsed_info: Dict[str, Any], ygo_service) -> Tuple[Optional[str], Optional[str], List[Any]]:
        """
        Attempts to find a matching card_id and variant_id from the database.
        Returns:
            (card_id, variant_id, candidates_list)
        If variant_id is None, it means ambiguity exists and candidates_list will contain the choices.
        """
        title = parsed_info['card_info'].get('title', '')
        number = parsed_info['card_info'].get('number', '')
        rarity = parsed_info['card_info'].get('rarity', '')

        # Clean title (remove (V.X) and suffix)
        import re
        clean_name = re.sub(r'\s*\(V\.\d+\s*-\s*[^\)]+\)', '', title)
        clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()

        # We need ygo_service to lookup
        api_card = None

        # Attempt lookup by name
        if clean_name:
            api_card = ygo_service.search_by_name(clean_name, language='en')
            if not api_card:
                # remove just the rarity if present
                clean_name = re.sub(r'\s*\([^\)]+(?:Rare|Common|Ultimate|Ghost|Prismatic)\)', '', title).strip()
                clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()
                api_card = ygo_service.search_by_name(clean_name, language='en')

        # Attempt lookup by set code if we didn't find by name
        if not api_card and number:
            pass

        if not api_card:
            return None, None, []

        card_id = str(api_card.id)

        from src.core.utils import generate_variant_id

        # Find matching variants
        candidates = []
        for v in api_card.card_sets:
            # Check number (set code) match
            if number:
                if number.lower() not in v.set_code.lower():
                    continue

            # Check rarity
            if rarity:
                db_rarity = v.set_rarity.lower()
                parsed_rarity = rarity.lower()
                # For exact matches, prioritize them later, but for filtering we need at least a substring
                if parsed_rarity != db_rarity and parsed_rarity not in db_rarity and db_rarity not in parsed_rarity:
                    continue

            candidates.append(v)

        # Try to find an exact match first to narrow down candidates
        if rarity:
            exact_matches = [v for v in candidates if v.set_rarity.lower() == rarity.lower()]
            if exact_matches:
                candidates = exact_matches

        if len(candidates) == 1:
            # Exact match
            v = candidates[0]
            var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
            return card_id, var_id, candidates

        return card_id, None, candidates

    def save_pricing_data(self, card_id: str, variant_id: str, html_date: str, parsed_data: Dict, save_daily: bool, save_offers: bool):
        card_id = str(card_id)

        if save_daily and 'prices' in parsed_data and parsed_data['prices']:
            if card_id not in self.daily_pricing: self.daily_pricing[card_id] = {}
            if variant_id not in self.daily_pricing[card_id]: self.daily_pricing[card_id][variant_id] = {}
            if 'cardmarket' not in self.daily_pricing[card_id][variant_id]: self.daily_pricing[card_id][variant_id]['cardmarket'] = {}

            for date_str, price in parsed_data['prices']:
                # Input format: DD.MM.YYYY
                iso_date = date_str
                try:
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        # YYYY-MM-DD
                        iso_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                except Exception:
                    pass
                self.daily_pricing[card_id][variant_id]['cardmarket'][iso_date] = price

            self._save_json(self.daily_pricing_file, self.daily_pricing)

        if save_offers and 'offers' in parsed_data and parsed_data['offers']:
            if card_id not in self.offers_pricing: self.offers_pricing[card_id] = {}
            if variant_id not in self.offers_pricing[card_id]: self.offers_pricing[card_id][variant_id] = {}
            if 'cardmarket' not in self.offers_pricing[card_id][variant_id]: self.offers_pricing[card_id][variant_id]['cardmarket'] = {}

            if not html_date:
                html_date = datetime.now().strftime("%Y-%m-%d")

            if html_date not in self.offers_pricing[card_id][variant_id]['cardmarket']:
                self.offers_pricing[card_id][variant_id]['cardmarket'][html_date] = {'offers': []}

            # Replace or extend offers? The prompt implies replacing the offers for that specific date snapshot.
            self.offers_pricing[card_id][variant_id]['cardmarket'][html_date]['offers'] = parsed_data['offers']

            self._save_json(self.offers_pricing_file, self.offers_pricing)

pricing_service = PricingService()
