from src.ui import dashboard


def test_pie_data_sorts_by_value_descending():
    data = dashboard.pie_data({'Rare': 5, 'Common': 20, 'Super Rare': 12})

    assert [d['name'] for d in data] == ['Common', 'Super Rare', 'Rare']
    assert [d['value'] for d in data] == [20, 12, 5]


def test_pie_data_keeps_small_distributions_intact():
    distribution = {f'Rarity {i}': i for i in range(1, dashboard.MAX_PIE_SLICES + 2)}

    data = dashboard.pie_data(distribution)

    assert len(data) == len(distribution)
    assert not any(d['name'].startswith('Other') for d in data)


def test_pie_data_folds_long_tail_into_other():
    # 12 categories: the 8 biggest stay, the remaining 4 collapse into one slice.
    distribution = {f'Rarity {i}': i for i in range(1, 13)}

    data = dashboard.pie_data(distribution)

    assert len(data) == dashboard.MAX_PIE_SLICES + 1
    assert data[-1]['name'] == 'Other (4)'
    assert data[-1]['value'] == 1 + 2 + 3 + 4
    # Nothing is lost or double counted.
    assert sum(d['value'] for d in data) == sum(distribution.values())


def test_pie_data_handles_empty_distribution():
    assert dashboard.pie_data({}) == []
