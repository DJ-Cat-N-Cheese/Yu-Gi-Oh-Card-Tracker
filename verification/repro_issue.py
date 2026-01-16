import sys
import os
import re

# Add src to path
sys.path.append(os.getcwd())

from src.core.utils import transform_set_code

def test_transform():
    print("Testing transform_set_code...")

    cases = [
        ("BP02-EN137", "DE", "BP02-DE137"),
        ("BP02-DE137", "EN", "BP02-EN137"),
        ("BP02-DE137", "DE", "BP02-DE137"),
        ("SDY-006", "DE", "SDY-006"), # Old code, no region
        ("RA01-EN054", "FR", "RA01-FR054"),
    ]

    for inp, lang, expected in cases:
        res = transform_set_code(inp, lang)
        print(f"transform('{inp}', '{lang}') -> '{res}' (Expected: '{expected}')")
        if res != expected:
            print("  FAIL!")
        else:
            print("  PASS")

def simulate_matching():
    print("\nSimulating matching logic...")

    # Mock Card Sets
    class MockSet:
        def __init__(self, code, name):
            self.set_code = code
            self.set_name = name

    card_sets = [
        MockSet("BP02-EN137", "Battle Pack 2: War of the Giants"),
        MockSet("LOB-EN001", "Legend of Blue Eyes White Dragon")
    ]

    set_options = {}
    for s in card_sets:
        set_options[s.set_code] = s.set_name

    print(f"Set Options: {set_options.keys()}")

    user_set_code = "BP02-DE137"
    user_lang = "DE"

    # Logic from open_collectors
    initial_base_code = None
    if user_set_code in set_options:
        initial_base_code = user_set_code
        print(f"Direct match found: {user_set_code}")
    else:
        found = False
        for base in set_options.keys():
            transformed = transform_set_code(base, user_lang)
            print(f"Checking base '{base}' -> transformed '{transformed}' vs user '{user_set_code}'")
            if transformed == user_set_code:
                initial_base_code = base
                found = True
                print(f"  Match found! base: {base}")
                break
        if not found:
            initial_base_code = list(set_options.keys())[0] if set_options else "Custom"
            print(f"  No match. Fallback to: {initial_base_code}")

if __name__ == "__main__":
    test_transform()
    simulate_matching()
