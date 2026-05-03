from src.services.pricing_service import pricing_service

code = """
<<<<<<< SEARCH
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

            # If standard filtering fails, try lenient abbreviation checks or partial matching for rarity
            if not rarity_filtered:
                lenient_filtered = [v for v in top_candidates if mapped_rarity in v.set_rarity.lower() or v.set_rarity.lower() in mapped_rarity]
                if len(lenient_filtered) == 1:
                    v = lenient_filtered[0]
                    var_id = getattr(v, "variant_id", None)
                    if not var_id:
                        var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
                    return card_id, var_id, lenient_filtered

        # Structure Deck strict fallback:
        # If there are multiple candidates but ONLY ONE base set code that exactly matches the input,
        # we still can't auto-resolve if rarities don't match exactly. But at least return the candidates.
        # Wait, if there are candidates but rarity is completely missing, return None and candidates.

        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates
=======
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

            # If standard filtering fails, try lenient abbreviation checks or partial matching for rarity
            if not rarity_filtered:
                lenient_filtered = [v for v in top_candidates if mapped_rarity in v.set_rarity.lower() or v.set_rarity.lower() in mapped_rarity]
                if len(lenient_filtered) == 1:
                    v = lenient_filtered[0]
                    var_id = getattr(v, "variant_id", None)
                    if not var_id:
                        var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
                    return card_id, var_id, lenient_filtered

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
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
