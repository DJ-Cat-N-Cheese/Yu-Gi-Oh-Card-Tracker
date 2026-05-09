
@pytest.mark.asyncio
async def test_pricing_service_cardmarket_parsing_fix3():
    await ygo_service.load_card_database('en')

    html = """
    <title>Mulcharmy Meowls (L26D) - Legendary Modern Decks 2026 - Yu-Gi-Oh!</title>
    <div class="row info-list-container">
        <dl class="labeled row mx-auto no-gutters">
            <dt class="col-6 col-xl-5">Number</dt>
            <dd class="col-6 col-xl-7">X13</dd>
            <dt class="col-6 col-xl-5">Printed in</dt>
            <dd class="col-6 col-xl-7">Legendary Modern Decks 2026</dd>
            <dt class="col-6 col-xl-5">Rarity</dt>
            <dd class="col-6 col-xl-7">Common</dd>
        </dl>
    </div>
    """

    parsed = pricing_service.parse_cardmarket_html(html)
    card_id, variant_id, candidates = pricing_service.resolve_card_variant(parsed, ygo_service)

    assert card_id == '87126721'
    assert variant_id == '35d103fd887be8acf73f250cadd3e626'
