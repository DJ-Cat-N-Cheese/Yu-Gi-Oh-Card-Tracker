import re

with open('src/services/ygo_api.py', 'r') as f:
    content = f.read()

# 1. Eliminate redundant pre-cleanup loop
new_content = content.replace(
    '''        # PRE-CLEANUP: Ensure all local sets have valid IDs before merging.
        # This prevents duplicate/missing/empty IDs from causing drops during deduplication.
        for l_card in local_cards:
            # Fallback default image id
            l_default_img = l_card.card_images[0].id if l_card.card_images else None

            for s in l_card.card_sets:
                # 1. Ensure image_id is present
                if s.image_id is None:
                    s.image_id = l_default_img

                # 2. Ensure variant_id is present and valid (not None or empty string)
                if not s.variant_id:
                    s.variant_id = generate_variant_id(
                        l_card.id, s.set_code, s.set_rarity, s.image_id
                    )''',
    '''        # PRE-CLEANUP loop removed to optimize O(N*M) checks.
        # Generation of missing image_id and variant_id is deferred to local_sets_map generation and custom card loops.'''
)

# 2. Move checks to map generation block
new_content = new_content.replace(
    '''                local_sets_map = {}
                for s in local_card.card_sets:
                    key = (s.set_code, s.set_rarity)
                    if key not in local_sets_map:
                        local_sets_map[key] = []
                    local_sets_map[key].append(s)''',
    '''                local_sets_map = {}
                l_default_img = local_card.card_images[0].id if local_card.card_images else None
                for s in local_card.card_sets:
                    if s.image_id is None:
                        s.image_id = l_default_img
                    if not s.variant_id:
                        s.variant_id = generate_variant_id(
                            local_card.id, s.set_code, s.set_rarity, s.image_id
                        )
                    key = (s.set_code, s.set_rarity)
                    if key not in local_sets_map:
                        local_sets_map[key] = []
                    local_sets_map[key].append(s)'''
)

# 3. Clean up redundant checks in merge map iteration
new_content = new_content.replace(
    '''                            # (Redundant safety check, already handled in pre-cleanup but harmless to keep if logic changes)
                            if local_s.image_id is None:
                                local_s.image_id = default_image_id
                            if not local_s.variant_id:
                                local_s.variant_id = generate_variant_id(
                                    api_card.id, local_s.set_code, local_s.set_rarity, local_s.image_id
                                )''',
    '''                            # Safety check removed. variant_id and image_id already handled during local_sets_map creation.'''
)

new_content = new_content.replace(
    '''                        if s.variant_id not in processed_local_sets:
                            # Ensure IDs for local orphans too
                            if s.image_id is None:
                                s.image_id = default_image_id
                            if s.variant_id is None:
                                s.variant_id = generate_variant_id(
                                    api_card.id, s.set_code, s.set_rarity, s.image_id
                                )
                            merged_sets.append(s)''',
    '''                        if s.variant_id not in processed_local_sets:
                            merged_sets.append(s)'''
)

# 4. Move checks to unmatched custom cards loop
new_content = new_content.replace(
    '''        # Add any local cards that were NOT in the API (e.g. custom cards)
        # We previously dropped them, but now we keep them to prevent data loss.
        for l_card in local_cards:
            if l_card.id not in processed_card_ids:
                merged_list.append(l_card)''',
    '''        # Add any local cards that were NOT in the API (e.g. custom cards)
        # We previously dropped them, but now we keep them to prevent data loss.
        for l_card in local_cards:
            if l_card.id not in processed_card_ids:
                l_default_img = l_card.card_images[0].id if l_card.card_images else None
                for s in l_card.card_sets:
                    if s.image_id is None:
                        s.image_id = l_default_img
                    if not s.variant_id:
                        s.variant_id = generate_variant_id(
                            l_card.id, s.set_code, s.set_rarity, s.image_id
                        )
                merged_list.append(l_card)'''
)

with open('src/services/ygo_api.py', 'w') as f:
    f.write(new_content)
