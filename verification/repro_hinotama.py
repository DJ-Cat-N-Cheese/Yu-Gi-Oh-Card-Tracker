import asyncio
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Mock Classes
@dataclass
class ApiCardSet:
    variant_id: str
    set_name: str
    set_code: str
    set_rarity: str
    image_id: int
    set_rarity_code: Optional[str] = None
    set_price: str = "0.00"

@dataclass
class ApiCard:
    id: int
    name: str
    card_sets: List[ApiCardSet]
    card_images: List[Any] = None

@dataclass
class ParsedRow:
    quantity: int
    name: str
    set_prefix: str
    number: str
    language: str
    rarity: str = "Common"
    rarity_abbr: str = "C"
    set_condition: str = "NM"
    first_edition: bool = False
    set_rarity: str = "Common"

# Mock Utilities
def normalize_set_code(code: str) -> str:
    m = re.match(r'^([A-Za-z0-9]+)-([A-Za-z]+)(\d+)$', code)
    if m:
        return f"{m.group(1)}-{m.group(3)}"
    m = re.match(r'^([A-Za-z0-9]+)-(\d+)$', code)
    if m:
        return code
    return code

def is_set_code_compatible(code: str, language: str) -> bool:
    return True # Allow everything for test

def get_legacy_code(prefix, number, language):
    if language.lower() == 'de':
        return f"{prefix}-G{number}" # Mock legacy mapping
    return None

# Mock Service
class MockYgoService:
    async def load_card_database(self, language: str):
        print(f"Loading DB for {language}")
        if language == 'en':
            return [
                ApiCard(
                    id=1001,
                    name="Blue-Eyes White Dragon",
                    card_sets=[
                        ApiCardSet("v1", "LOB", "LOB-001", "Ultra Rare", 1)
                    ]
                ),
                ApiCard(
                    id=1002,
                    name="Raigeki",
                    card_sets=[
                        ApiCardSet("v2", "LOB", "LOB-021", "Super Rare", 2)
                    ]
                ),
                 ApiCard(
                    id=1003,
                    name="Hinotama Soul",
                    card_sets=[
                        ApiCardSet("v3", "LOB", "LOB-076", "Common", 3)
                    ]
                )
            ]
        elif language == 'de':
            # Missing LOB-G021 (Hinotama Soul in German Legacy)
            # Maybe has others
            return [
                ApiCard(
                    id=1001,
                    name="Blauäugiger w. Drache",
                    card_sets=[
                        ApiCardSet("v1_de", "LOB", "LOB-G001", "Ultra Rare", 1)
                    ]
                )
            ]
        return []

# Reproduction Controller
class ReproController:
    def __init__(self):
        self.db_lookup = {}
        self.ambiguous_rows = []
        self.failed_rows = []
        self.ygo_service = MockYgoService()

    async def process(self):
        # Input: Hinotama Soul (German Legacy Code LOB-G021? Or LOB-021?)
        # User says "Hinotama Soul" is missing.
        # Let's assume input is "LOB-G021" (Legacy German)
        # Note: In real life, LOB-G021 is Hinotama Soul? I need to verify mapping.
        # But let's assume collision with Raigeki (LOB-021).

        row = ParsedRow(
            quantity=1,
            name="Hinotama Soul",
            set_prefix="LOB",
            number="021", # Parser extracts 021 from LOB-G021?
            language="DE",
            set_rarity="Common"
        )
        # If parser extracts "021" from "LOB-G021", then base code is LOB-021.

        required_langs = {'de', 'en'}

        for db_lang in required_langs:
             cards = await self.ygo_service.load_card_database(db_lang)
             for card in cards:
                 for s in card.card_sets:
                     code = s.set_code
                     entry = {'rarity': s.set_rarity, 'card': card, 'variant': s}

                     # Key 1: Exact Code
                     if code not in self.db_lookup: self.db_lookup[code] = []
                     self.db_lookup[code].append(entry)

                     # Key 2: Base Code
                     base_code = normalize_set_code(code)
                     if base_code != code:
                         if base_code not in self.db_lookup: self.db_lookup[base_code] = []
                         self.db_lookup[base_code].append(entry)

        # Lookup
        base_code = f"{row.set_prefix}-{row.number}" # "LOB-021"
        print(f"Looking up Base Code: {base_code}")

        all_siblings = []
        if base_code in self.db_lookup:
            for entry in self.db_lookup[base_code]:
                all_siblings.append(entry)

        print(f"Found {len(all_siblings)} siblings")
        for s in all_siblings:
            print(f" - {s['card'].name} ({s['variant'].set_code})")

        if not all_siblings:
            print("FAILED: No siblings found (Card Missing)")
        elif all_siblings[0]['card'].name != "Hinotama Soul":
            print(f"MISMATCH: Expected Hinotama Soul, got {all_siblings[0]['card'].name}")

if __name__ == "__main__":
    asyncio.run(ReproController().process())
