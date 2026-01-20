import re

# Mock Utils
def normalize_set_code(code: str) -> str:
    # Basic logic from memory of standard behavior
    m = re.match(r'^([A-Za-z0-9]+)-([A-Za-z]+)(\d+)$', code)
    if m:
        return f"{m.group(1)}-{m.group(3)}"
    m = re.match(r'^([A-Za-z0-9]+)-(\d+)$', code)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return code

def is_set_code_compatible(code, lang):
    return True # simplified

def get_legacy_code(prefix, number, lang):
    return f"{prefix}-G{number}" if lang == 'DE' else None

# Mock Models
class ApiCard:
    def __init__(self, id, name, sets):
        self.id = id
        self.name = name
        self.card_sets = sets

class ApiCardSet:
    def __init__(self, variant_id, set_code, set_rarity):
        self.variant_id = variant_id
        self.set_code = set_code
        self.set_rarity = set_rarity
        self.image_id = 0

# Test Setup
def run_test():
    print("--- Test Start ---")

    # DB Data
    # EN DB: LOB-021 is Raigeki. Hinotama Soul is LOB-076.
    card_raigeki = ApiCard(1, "Raigeki", [
        ApiCardSet("v1", "LOB-EN021", "Super Rare"),
        ApiCardSet("v2", "LOB-021", "Super Rare") # Legacy EN often same
    ])

    card_hinotama = ApiCard(2, "Hinotama Soul", [
        ApiCardSet("v3", "LOB-EN076", "Common")
    ])

    # DE DB: LOB-G021 (Legacy) might be Hinotama Soul (hypothetically)
    # But let's assume DE DB is MISSING this legacy code,
    # OR DE DB has "LOB-DE021" which is Raigeki (standardized).
    # If legacy sets had different numbering, we have a problem.
    # Fact Check: LOB German (LOB-G) numbering matches EN (LOB-000)?
    # Actually LOB-G001 is Blue-Eyes (same as LOB-001).
    # So numbering is usually consistent.
    # BUT, if "Hinotama Soul" disappeared, maybe the user input code is wrong?
    # Or maybe the code "LOB-G021" exists in input, but NO DB has it.

    # Let's assume Input is: Hinotama Soul | LOB | G021 (parsed as Prefix=LOB, Number=021, Lang=DE? No, G021 implies parsing needs to handle letter)

    # Parser usually splits: Prefix "LOB", Number "021", Language "DE"?
    # If the file says "LOB-G021", parsing might be tricky.
    # Assuming Parser extracts: Prefix=LOB, Number=021, Lang=DE.

    # Case 1: Numbering Mismatch
    # If Input LOB-021 (derived from G021) = Hinotama Soul in User's mind/reality (Legacy)
    # But in API/DB LOB-021 = Raigeki.
    # Then resolution matches Raigeki.
    # User sees "Raigeki" in list? User says "Hinotama Soul is gone".
    # If "Hinotama Soul" isn't in the list, it means it was filtered out or misidentified.

    db_en = [card_raigeki, card_hinotama]
    db_de = [] # Missing data

    db_lookup = {}

    # Build Lookup (EN)
    for card in db_en:
        for s in card.card_sets:
            code = s.set_code
            entry = {'rarity': s.set_rarity, 'card': card, 'variant': s}

            if code not in db_lookup: db_lookup[code] = []
            db_lookup[code].append(entry)

            base = normalize_set_code(code)
            if base != code:
                if base not in db_lookup: db_lookup[base] = []
                db_lookup[base].append(entry)

    # Process Row
    row_prefix = "LOB"
    row_number = "021" # Assuming parser extracted 021 from G021
    row_lang = "DE"

    base_code = f"{row_prefix}-{row_number}" # LOB-021
    print(f"Looking up Base Code: {base_code}")

    all_siblings = []
    if base_code in db_lookup:
        for entry in db_lookup[base_code]:
            print(f"Found Match: {entry['card'].name} ({entry['variant'].set_code})")
            all_siblings.append(entry)

    if not all_siblings:
        print("No siblings found.")
    else:
        print(f"Resolved to: {[s['card'].name for s in all_siblings]}")

if __name__ == "__main__":
    run_test()
