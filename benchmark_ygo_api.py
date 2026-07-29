import time
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.services.ygo_api import YugiohService
from src.core.models import ApiCard, ApiCardSet, ApiCardImage

def create_mock_data(num_cards=10000, num_sets_per_card=5):
    cards = []
    for i in range(num_cards):
        sets = []
        for j in range(num_sets_per_card):
            # some missing variant_id
            variant_id = None if j % 2 == 0 else f"var_{i}_{j}"
            # some missing image_id
            image_id = None if j % 3 == 0 else 1000 + j

            sets.append(ApiCardSet(
                set_name=f"Set {j}",
                set_code=f"SET-EN{j:03d}",
                set_rarity="Common",
                set_price="0.00",
                image_id=image_id,
                variant_id=variant_id
            ))

        card = ApiCard(
            id=i,
            name=f"Card {i}",
            type="Normal Monster",
            frameType="normal",
            desc="A card.",
            race="Spellcaster",
            atk=2500,
            def_=2100,
            card_images=[
                ApiCardImage(id=1000 + i, image_url="http://example.com/1.jpg", image_url_small="http://example.com/1s.jpg")
            ],
            card_sets=sets
        )
        cards.append(card)
    return cards

def run_benchmark():
    service = YugiohService()

    # create large lists
    print("Creating mock data...")
    local_cards = create_mock_data(10000, 10)
    api_cards = create_mock_data(10000, 10)

    print("Starting benchmark...")
    start_time = time.time()
    service._merge_database_data(local_cards, api_cards)
    end_time = time.time()

    print(f"Merge took: {end_time - start_time:.4f} seconds")

if __name__ == '__main__':
    run_benchmark()
