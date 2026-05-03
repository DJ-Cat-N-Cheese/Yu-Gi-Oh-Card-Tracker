from src.services.pricing_service import pricing_service

code = """
<<<<<<< SEARCH
            # 4. Aggressive Set Code Lookup
            # If name lookup completely fails, but we have a set code.
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
=======
            # 4. Aggressive Set Code Lookup
            # If name lookup completely fails, but we have a set code.
            # Handle cases where structure decks use ENM10 vs EN010
            if not api_card and target_set_code and '-' in target_set_code:
                # E.g. L26D-EN010 -> base prefix L26D
                prefix = target_set_code.split('-')[0].upper()
                # Extract trailing digits using regex
                match = re.search(r'(\d+)$', target_set_code)
                if match:
                    digits = match.group(1)
                    # Search database for anything matching prefix and digits
                    # But since there can be multiple cards matching (e.g. L26D-ENS10 vs L26D-ENM10),
                    # we must also partially match the name or just return the first one if only one exists.
                    # Given that we only fall back here if the name lookup fails, we will gather all candidates
                    # and see if one's name has high similarity to the target name.
                    candidates = []
                    for c in ygo_service._cards_cache.get('en', []):
                        for v in c.card_sets:
                            if v.set_code.startswith(prefix) and v.set_code.endswith(digits):
                                candidates.append(c)
                                break
                    if len(candidates) == 1:
                        api_card = candidates[0]
                    elif len(candidates) > 1:
                        # Try to find the best name match
                        def compute_similarity(str1, str2):
                            if not str1 or not str2: return 0
                            s1, s2 = str1.lower().strip(), str2.lower().strip()
                            if s1 == s2: return 1.0
                            if s1 in s2 or s2 in s1: return 0.8
                            w1, w2 = set(s1.split()), set(s2.split())
                            if w1 and w2:
                                return len(w1.intersection(w2)) / len(w1.union(w2))
                            return 0

                        best_score = 0
                        best_candidate = None
                        for c in candidates:
                            score = compute_similarity(clean_name, c.name)
                            if score > best_score:
                                best_score = score
                                best_candidate = c
                        if best_score > 0:
                            api_card = best_candidate

        if not api_card:
            return None, None, []
>>>>>>> REPLACE
"""

import sys
with open('patch_tmp.txt', 'w') as f:
    f.write(code)
