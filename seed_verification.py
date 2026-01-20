import json
import os
import hashlib
from typing import Optional

def generate_variant_id(card_id: int, set_code: str, rarity: str, image_id: Optional[int] = None) -> str:
    s_code = set_code.strip().upper()
    s_rarity = rarity.strip().lower()
    s_img = str(image_id) if image_id is not None else ""
    raw_str = f"{card_id}|{s_code}|{s_rarity}|{s_img}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

DB_DIR = "data/db"
COL_DIR = "data/collections"
LANG = "en"
DB_FILE = os.path.join(DB_DIR, f"card_db_{LANG}.json")
DB_FILE_DEFAULT = os.path.join(DB_DIR, "card_db.json") # Also overwrite this
COL_FILE = os.path.join(COL_DIR, "test_collection.json")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(COL_DIR, exist_ok=True)

# 1. Seed DB
cards = [
    {
        "id": 1001,
        "name": "British Card",
        "type": "Normal Monster",
        "frameType": "normal",
        "desc": "Card with GB language.",
        "atk": 1000,
        "def": 1000,
        "level": 4,
        "race": "Warrior",
        "attribute": "EARTH",
        "card_sets": [
            {
                "set_name": "British Set",
                "set_code": "BST-GB001",
                "set_rarity": "Common",
                "set_price": "1.00"
            }
        ],
        "card_images": [{"id": 1001, "image_url": "", "image_url_small": ""}]
    },
    {
        "id": 1002,
        "name": "German Card",
        "type": "Normal Monster",
        "frameType": "normal",
        "desc": "Card with DE language.",
        "atk": 1000,
        "def": 1000,
        "level": 4,
        "race": "Warrior",
        "attribute": "EARTH",
        "card_sets": [
            {
                "set_name": "German Set",
                "set_code": "GST-DE001",
                "set_rarity": "Common",
                "set_price": "1.00"
            }
        ],
        "card_images": [{"id": 1002, "image_url": "", "image_url_small": ""}]
    }
]

with open(DB_FILE, 'w') as f:
    json.dump(cards, f, indent=2)

with open(DB_FILE_DEFAULT, 'w') as f:
    json.dump(cards, f, indent=2)

# 2. Seed Collection
col_data = {
    "name": "test_collection",
    "cards": [
        {
            "card_id": 1001,
            "name": "British Card",
            "total_quantity": 1,
            "variants": [
                {
                    "variant_id": generate_variant_id(1001, "BST-GB001", "Common", 1001),
                    "set_code": "BST-GB001",
                    "rarity": "Common",
                    "image_id": 1001,
                    "entries": [
                        {
                            "language": "GB",
                            "condition": "Near Mint",
                            "first_edition": True,
                            "quantity": 1,
                            "purchase_date": "2023-01-01"
                        }
                    ]
                }
            ]
        },
        {
            "card_id": 1002,
            "name": "German Card",
            "total_quantity": 1,
            "variants": [
                {
                    "variant_id": generate_variant_id(1002, "GST-DE001", "Common", 1002),
                    "set_code": "GST-DE001",
                    "rarity": "Common",
                    "image_id": 1002,
                    "entries": [
                        {
                            "language": "DE",
                            "condition": "Near Mint",
                            "first_edition": True,
                            "quantity": 1,
                            "purchase_date": "2023-01-01"
                        }
                    ]
                }
            ]
        }
    ]
}

with open(COL_FILE, 'w') as f:
    json.dump(col_data, f, indent=2)

print("Seeding complete.")
