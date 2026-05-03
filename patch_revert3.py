from src.services.pricing_service import pricing_service

code = """
<<<<<<< SEARCH
        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates
=======
        # If there's only 1 top candidate (either naturally or after rarity filtering) and it's a reasonably strong match, resolve it automatically
        if len(top_candidates) == 1 and top_score >= 40:
            v = top_candidates[0]
            var_id = getattr(v, "variant_id", None)
            if not var_id:
                var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
            return card_id, var_id, top_candidates

        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
