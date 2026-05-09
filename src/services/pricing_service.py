import json
import logging
import os
import re
import asyncio
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

        # If the number is just a short 3-digit string (e.g., "078"), it's missing the set prefix.
        # We can extract the "printed_in" set name from the definition list and map it to a set code prefix if possible.
        printed_in = data['card_info'].get('printed_in', '')
        number = data['card_info'].get('number', '')

        # We can also attempt to extract the set prefix from the URL inside the HTML comments if it exists
        # e.g., <!-- saved from url=(0078)https://www.cardmarket.com/en/YuGiOh/Products/Singles/Maze-of-Millennia/RESCUE -->
        url_match = re.search(r'saved from url=\(\d+\)(https?://[^\s]+)', html_text)
        if url_match:
            data['card_info']['url'] = url_match.group(1).split('-->')[0].strip()

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

    def _infer_target_set_code(self, parsed_info: Dict[str, Any], ygo_service) -> str:
        number = parsed_info['card_info'].get('number', '').strip()
        printed_in = parsed_info['card_info'].get('printed_in', '').strip()
        url = parsed_info['card_info'].get('url', '').strip()

        if not number:
            return ""

        if '-' in number:
            return number

        prefix = None

        if printed_in:
            for c in ygo_service._cards_cache.get('en', []):
                for v in c.card_sets:
                    if v.set_name:
                        sn_lower = v.set_name.lower()
                        pi_lower = printed_in.lower()
                        if pi_lower in sn_lower or sn_lower in pi_lower:
                            if '-' in v.set_code:
                                prefix = v.set_code.split('-')[0]
                                break
                if prefix:
                    break

        if not prefix and url:
            try:
                url_slug = url.split('/')[-2].replace('-', ' ').lower()
                for c in ygo_service._cards_cache.get('en', []):
                    for v in c.card_sets:
                        if v.set_name and url_slug in v.set_name.lower():
                            if '-' in v.set_code:
                                prefix = v.set_code.split('-')[0]
                                break
                    if prefix:
                        break
            except IndexError:
                pass

        if prefix:
            # Assuming English region if it's just numbers
            return f"{prefix}-EN{number}" if number.isdigit() and len(number) <= 3 else f"{prefix}-{number}"

        return number

    def resolve_card_variant(self, parsed_info: Dict[str, Any], ygo_service) -> Tuple[Optional[str], Optional[str], List[Any]]:
        """
        Attempts to find a matching card_id and variant_id from the database.
        Returns:
            (card_id, variant_id, candidates_list)
        If variant_id is None, it means ambiguity exists and candidates_list will contain the choices.
        """
        title = parsed_info['card_info'].get('title', '')
        rarity = parsed_info['card_info'].get('rarity', '')
        target_set_code = self._infer_target_set_code(parsed_info, ygo_service)
        parsed_info['card_info']['target_set_code'] = target_set_code

        # Clean title (remove (V.X) and suffix)
        import re
        clean_name = re.sub(r'\s*\(V\.\d+(?:\s*-\s*[^\)]+)?\)', '', title)
        clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()

        api_card = None

        # 1. Primary Lookup: Set Code
        if target_set_code and '-' in target_set_code:
            for c in ygo_service._cards_cache.get('en', []):
                for v in c.card_sets:
                    if target_set_code.lower() == v.set_code.lower() or target_set_code.lower() in v.set_code.lower():
                        api_card = c
                        break
                if api_card:
                    break

        # 2. Fallback Lookup: Name
        if not api_card and clean_name:
            # Strip common suffixes that might be lingering
            clean_name = re.sub(r'\s*-\s*Yu-Gi-Oh!$', '', clean_name, flags=re.IGNORECASE).strip()
            api_card = ygo_service.search_by_name(clean_name, language='en')

            if not api_card:
                # Try progressively splitting by " - " and matching parts
                parts = clean_name.split(' - ')
                for i in range(len(parts), 0, -1):
                    attempt = ' - '.join(parts[:i]).strip()
                    api_card = ygo_service.search_by_name(attempt, language='en')
                    if api_card:
                        break

            if not api_card:
                # remove just the rarity if present
                clean_name = re.sub(r'\s*\([^\)]+(?:Rare|Common|Ultimate|Ghost|Prismatic)\)', '', title).strip()
                clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()
                clean_name = re.sub(r'\s*-\s*Yu-Gi-Oh!$', '', clean_name, flags=re.IGNORECASE).strip()
                api_card = ygo_service.search_by_name(clean_name, language='en')

                if not api_card:
                    # Try progressively splitting by " - " again on the fallback name
                    parts = clean_name.split(' - ')
                    for i in range(len(parts), 0, -1):
                        attempt = ' - '.join(parts[:i]).strip()
                        api_card = ygo_service.search_by_name(attempt, language='en')
                        if api_card:
                            break

            if not api_card:
                # One last attempt: Cardmarket often puts set prefixes or rarity codes in parentheses in the title
                # e.g., "Mulcharmy Meowls (L26D)". Try aggressively stripping ANY parentheses blocks before the set name.
                attempt = re.sub(r'\s*\([^)]+\)', '', clean_name).strip()
                api_card = ygo_service.search_by_name(attempt, language='en')
                if not api_card:
                    # Also try stripping it and THEN splitting by " - "
                    parts = attempt.split(' - ')
                    for i in range(len(parts), 0, -1):
                        sub_attempt = ' - '.join(parts[:i]).strip()
                        api_card = ygo_service.search_by_name(sub_attempt, language='en')
                        if api_card:
                            break

        if not api_card:
            return None, None, []

        card_id = str(api_card.id)

        from src.core.utils import generate_variant_id

        # Robust Variant Scoring Strategy
        scored_variants = []
        printed_in = parsed_info['card_info'].get('printed_in', '')
        url = parsed_info['card_info'].get('url', '')

        def compute_similarity(str1, str2):
            if not str1 or not str2: return 0
            s1, s2 = str1.lower().strip(), str2.lower().strip()
            if s1 == s2: return 1.0
            if s1 in s2 or s2 in s1: return 0.8
            # Simple word intersection fallback
            w1, w2 = set(s1.split()), set(s2.split())
            if w1 and w2:
                return len(w1.intersection(w2)) / len(w1.union(w2))
            return 0

        for v in api_card.card_sets:
            score = 0

            # 1. Number / Target Set Code Match
            if target_set_code:
                n_clean = target_set_code.lower().strip()
                vc_clean = v.set_code.lower().strip()
                if n_clean == vc_clean:
                    score += 50
                elif n_clean in vc_clean or vc_clean in n_clean:
                    if vc_clean.endswith(n_clean) or n_clean.endswith(vc_clean):
                        score += 40
                    else:
                        score += 20

            # 2. Set Name Match
            set_name_score = 0
            if printed_in and v.set_name:
                set_name_score = max(set_name_score, compute_similarity(printed_in, v.set_name))

            if url and v.set_name:
                try:
                    url_slug = url.split('/')[-2].replace('-', ' ').lower()
                    set_name_score = max(set_name_score, compute_similarity(url_slug, v.set_name))
                except IndexError:
                    pass

            score += set_name_score * 40

            # 3. Rarity Match
            if rarity:
                r_clean = rarity.lower().strip()
                vr_clean = v.set_rarity.lower().strip()

                if r_clean == vr_clean:
                    score += 30
                elif r_clean in vr_clean or vr_clean in r_clean:
                    score += 15

            if score > 0:
                scored_variants.append((score, v))

        # Sort by score descending
        scored_variants.sort(key=lambda x: x[0], reverse=True)

        if not scored_variants:
            return card_id, None, api_card.card_sets

        top_score = scored_variants[0][0]
        # Gather all variants that tie for the top score (could be alternate arts of the exact same set)
        top_candidates = [v for s, v in scored_variants if s == top_score]

        # If there's only 1 top candidate and it's a reasonably strong match, resolve it automatically
        if len(top_candidates) == 1 and top_score >= 40:
            v = top_candidates[0]
            var_id = getattr(v, "variant_id", None)
            if not var_id:
                var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
            return card_id, var_id, top_candidates

        # Filter by rarity from HTML (using existing mapping table) before deferring to ambiguity
        if len(top_candidates) > 1 and rarity:
            from src.services.yugipedia_service import YugipediaService
            mapped_rarity = YugipediaService.RARITY_MAP.get(rarity.strip(), rarity.strip()).lower()
            rarity_filtered = [v for v in top_candidates if v.set_rarity.lower() == mapped_rarity]

            if len(rarity_filtered) == 1:
                v = rarity_filtered[0]
                var_id = getattr(v, "variant_id", None)
                if not var_id:
                    var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
                return card_id, var_id, rarity_filtered

        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates

    def save_pricing_data(self, card_id: str, variant_id: str, html_date: str, parsed_data: Dict, save_daily: bool, save_offers: bool, ygo_service=None):
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

        # Update cardmarket_url in the main card database
        if ygo_service and variant_id:
            cm_url = parsed_data.get('card_info', {}).get('url')
            if cm_url:
                asyncio.create_task(self._update_cardmarket_url(card_id, variant_id, cm_url, ygo_service))

    async def _update_cardmarket_url(self, card_id: str, variant_id: str, url: str, ygo_service):
        try:
            cards = await ygo_service.load_card_database("en")
            card = next((c for c in cards if str(c.id) == card_id), None)
            if card:
                variant = next((v for v in card.card_sets if v.variant_id == variant_id), None)
                if variant:
                    variant.cardmarket_url = url
                    await ygo_service.save_card_database(cards, "en")
                    logger.info(f"Updated cardmarket_url for variant {variant_id} of card {card_id}")
        except Exception as e:
            logger.error(f"Failed to update cardmarket_url: {e}")

pricing_service = PricingService()
