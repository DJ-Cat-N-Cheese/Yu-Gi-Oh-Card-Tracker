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

        # If there's only 1 top candidate (either naturally or after rarity filtering) and it's a reasonably strong match, resolve it automatically
        if len(top_candidates) == 1 and top_score >= 40:
            v = top_candidates[0]
            var_id = getattr(v, "variant_id", None)
            if not var_id:
                var_id = generate_variant_id(api_card.id, v.set_code, v.set_rarity, v.image_id)
            return card_id, var_id, top_candidates

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

        # Ambiguous (either tied scores or very weak matches)
        return card_id, None, top_candidates
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
