import logging
import random
import os
from typing import List, Optional

from src.services.ygo_api import ygo_service
from src.core.persistence import persistence
from src.core.models import Collection, CollectionCard, CollectionVariant, CollectionEntry, ApiCard
from src.core.utils import generate_variant_id, transform_set_code

logger = logging.getLogger(__name__)

LANGUAGES = ["EN", "DE", "FR", "IT", "JP"]
CONDITIONS = ["Mint", "Near Mint", "Played", "Damaged"]

class SampleGenerator:
    async def generate_sample_collection(self, filename: str = "sample_collection.json") -> int:
        """
        Generates a diverse sample collection and saves it.
        Returns the number of variants generated.
        """
        logger.info("Initializing generation...")

        # 1. Ensure DB is loaded
        logger.info("Loading Card Database...")
        cards = await ygo_service.load_card_database("en")

        if len(cards) == 0:
            logger.error("No cards found.")
            return 0

        # 2. Select Candidates
        valid_cards = [c for c in cards if c.card_sets and len(c.card_sets) > 0]

        rich_cards = [c for c in valid_cards if (c.card_images and len(c.card_images) > 1) or len(c.card_sets) > 5]

        candidates = []
        if len(rich_cards) >= 50:
            candidates = random.sample(rich_cards, 50)
        else:
            candidates = rich_cards + random.sample([c for c in valid_cards if c not in rich_cards], 50 - len(rich_cards))

        logger.info(f"Selected {len(candidates)} cards for collection.")

        collection_cards = []
        total_variants_count = 0

        for card in candidates:
            variants = []
            num_variants = random.randint(3, 5)
            available_sets = card.card_sets

            for _ in range(num_variants):
                base_set = random.choice(available_sets)
                lang = random.choice(LANGUAGES)

                final_set_code = transform_set_code(base_set.set_code, lang)

                image_id = base_set.image_id
                if image_id is None and card.card_images:
                    image_id = card.card_images[0].id

                var_id = generate_variant_id(card.id, final_set_code, base_set.set_rarity, image_id)

                if any(v.variant_id == var_id for v in variants):
                    continue

                entries = []
                qty = random.randint(1, 3)
                cond = random.choice(CONDITIONS)
                first_ed = random.choice([True, False])

                entries.append(CollectionEntry(
                    condition=cond,
                    language=lang,
                    first_edition=first_ed,
                    quantity=qty,
                    storage_location=f"Box {random.choice(['A', 'B', 'C'])}",
                    purchase_price=round(random.uniform(1.0, 50.0), 2),
                    market_value=round(random.uniform(1.0, 50.0), 2)
                ))

                if random.random() < 0.2:
                     entries.append(CollectionEntry(
                        condition=random.choice([c for c in CONDITIONS if c != cond]),
                        language=lang,
                        first_edition=first_ed,
                        quantity=1
                    ))

                variants.append(CollectionVariant(
                    variant_id=var_id,
                    set_code=final_set_code,
                    rarity=base_set.set_rarity,
                    image_id=image_id,
                    entries=entries
                ))

            if variants:
                collection_cards.append(CollectionCard(
                    card_id=card.id,
                    name=card.name,
                    variants=variants
                ))
                total_variants_count += len(variants)

        # 3. Construct Collection
        collection = Collection(
            name="Sample Collection",
            description="A generated sample collection with diverse cards.",
            cards=collection_cards
        )

        # 4. Save
        persistence.save_collection(collection, filename)
        logger.info(f"Saved collection to {filename} with {total_variants_count} variants.")

        return total_variants_count

sample_generator = SampleGenerator()
