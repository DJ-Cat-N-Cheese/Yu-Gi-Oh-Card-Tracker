from src.core.models import Collection, CollectionCard, CollectionVariant, CollectionEntry
from src.core.persistence import persistence

def setup():
    col = Collection(name="Test Collection")

    entry = CollectionEntry(quantity=1, condition="Near Mint", first_edition=True, language="en", storage_location="Binder 1")
    variant = CollectionVariant(variant_id="V123", set_code="LOB-001", rarity="Ultra Rare", entries=[entry])
    card = CollectionCard(card_id=123, name="Blue-Eyes White Dragon", variants=[variant])

    col.cards.append(card)

    persistence.save_collection(col, "test_col.json")
    persistence.save_ui_state({'collection_selected_file': "test_col.json"})

setup()
