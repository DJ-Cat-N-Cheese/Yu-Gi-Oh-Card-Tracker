import sys

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Apply fix for the potential IndexError on empty database
    search = "state['original_db_snapshot'] = [c.model_copy(deep=True) for c in cards] if hasattr(cards[0], 'model_copy') else copy.deepcopy(cards)"
    replace = "state['original_db_snapshot'] = [c.model_copy(deep=True) for c in cards] if cards and hasattr(cards[0], 'model_copy') else copy.deepcopy(cards)"

    if search in content:
        content = content.replace(search, replace)
        with open(filepath, 'w') as f:
            f.write(content)
        print("Patched successfully")
    else:
        print("Search string not found")

patch_file('src/ui/layout.py')
