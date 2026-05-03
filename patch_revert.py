from src.services.pricing_service import pricing_service

code = """
<<<<<<< SEARCH
        # Structure Deck strict fallback:
        # If there are multiple candidates but they ALL share exactly the same set code as the parsed target,
        # AND we could not filter them by rarity, it means Cardmarket provides a generic rarity (e.g., 'Common')
        # while the Database provides explicit foil rarities (e.g., 'Ultra Rare', 'Secret Rare').
        # In this specific case, if they all share the EXACT same set code, we can just default to the first candidate.
        if len(top_candidates) > 1 and target_set_code:
            tc_clean = target_set_code.lower().strip()
            all_match = all(tc_clean == v.set_code.lower().strip() for v in top_candidates)
            if all_match:
                # Default to the first candidate (which is functionally identical since they share the same set code)
                v = top_candidates[0]
                var_id = getattr(v, "variant_id", None)
                if not var_id:
                    var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
                return card_id, var_id, [v]

        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates
=======
        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
