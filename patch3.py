from src.services.pricing_service import pricing_service

code = """
<<<<<<< SEARCH
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
=======
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
                        # If we match the set code exactly, make sure we aren't heavily mismatching the name!
                        # e.g. Cardmarket RA03-EN004 is Dark Paladin but Database RA03-EN004 is Deep Sea Diva
                        if clean_name:
                            cn_lower = clean_name.lower()
                            db_name = c.name.lower()
                            # If they are completely different (not substring of each other), do not match
                            if cn_lower not in db_name and db_name not in cn_lower:
                                # Check if they share any significant word
                                w1, w2 = set(cn_lower.split()), set(db_name.split())
                                if not w1.intersection(w2):
                                    continue # Force fallback to name lookup
                        api_card = c
                        break
                if api_card:
                    break
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
