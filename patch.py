from src.services.pricing_service import pricing_service

code = """
<<<<<<< SEARCH
        # 2. Fallback Lookup: Name
        if not api_card and clean_name:
            api_card = ygo_service.search_by_name(clean_name, language='en')
            if not api_card:
                # remove just the rarity if present
                clean_name = re.sub(r'\s*\([^\)]+(?:Rare|Common|Ultimate|Ghost|Prismatic)\)', '', title).strip()
                clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()
                api_card = ygo_service.search_by_name(clean_name, language='en')

        if not api_card:
            return None, None, []
=======
        # 2. Fallback Lookup: Name
        if not api_card and clean_name:
            api_card = ygo_service.search_by_name(clean_name, language='en')
            if not api_card:
                # remove just the rarity if present
                clean_name = re.sub(r'\s*\([^\)]+(?:Rare|Common|Ultimate|Ghost|Prismatic)\)', '', title).strip()
                clean_name = re.split(r'\s*-\s*YGO Singles', clean_name)[0].strip()
                api_card = ygo_service.search_by_name(clean_name, language='en')

            # 3. Aggressive Fallback Name Lookup:
            # Handle cases where Cardmarket appends ' - <Set Name>' to the title
            if not api_card and clean_name:
                parts = clean_name.split(' - ')
                for i in range(len(parts), 0, -1):
                    candidate_name = ' - '.join(parts[:i]).strip()
                    api_card = ygo_service.search_by_name(candidate_name, language='en')
                    if api_card:
                        break

            # 4. Aggressive Set Code Lookup
            # If name lookup completely fails (e.g., translation differs), but we have a set code.
            # Handle cases where structure decks use ENM10 vs EN010
            if not api_card and target_set_code and '-' in target_set_code:
                # E.g. L26D-EN010 -> base prefix L26D
                prefix = target_set_code.split('-')[0].upper()
                # Extract trailing digits using regex
                match = re.search(r'(\d+)$', target_set_code)
                if match:
                    digits = match.group(1)
                    # Search database for anything matching prefix and digits
                    for c in ygo_service._cards_cache.get('en', []):
                        for v in c.card_sets:
                            if v.set_code.startswith(prefix) and v.set_code.endswith(digits):
                                api_card = c
                                break
                        if api_card:
                            break

        if not api_card:
            return None, None, []
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
