import asyncio
from typing import Optional, List, Dict
import time
from dataclasses import dataclass

class MockChangelogManager:
    def load_history(self, filename):
        return [
            {"type": "single", "timestamp": 100, "card_data": {"card_id": 1}},
            {"type": "single", "timestamp": 200, "card_data": {"card_id": 2, "variant_id": "var_2"}},
            {"type": "batch", "timestamp": 300, "changes": [
                {"card_data": {"card_id": 3, "variant_id": "var_3"}}
            ]},
        ]

class MockApiCard:
    def __init__(self, id):
        self.id = id

class MockCard:
    def __init__(self, api_card, variant_id=None):
        self.api_card = api_card
        self.variant_id = variant_id

class MockApp:
    def __init__(self):
        self.state = {
            'sort_by': 'Newest',
            'sort_descending': True,
            'selected_file': 'dummy.json',
            'view_scope': 'consolidated'
        }
        self.changelog_manager = MockChangelogManager()

    def apply_filters(self, res):
        key = self.state['sort_by']
        reverse = self.state.get('sort_descending', False)

        if key == 'Newest':
            timestamp_map = {}
            if self.state['selected_file']:
                history = self.changelog_manager.load_history(self.state['selected_file'])
                for entry in history:
                    ts = entry.get('timestamp', 0)
                    if entry.get('type') == 'single':
                        card_data = entry.get('card_data', {})
                        card_id = card_data.get('card_id')
                        var_id = card_data.get('variant_id')
                        if card_id is not None:
                            timestamp_map[card_id] = max(timestamp_map.get(card_id, 0), ts)
                        if var_id is not None:
                            timestamp_map[var_id] = max(timestamp_map.get(var_id, 0), ts)
                    elif entry.get('type') == 'batch':
                        for change in entry.get('changes', []):
                            card_data = change.get('card_data', {})
                            card_id = card_data.get('card_id')
                            var_id = card_data.get('variant_id')
                            if card_id is not None:
                                timestamp_map[card_id] = max(timestamp_map.get(card_id, 0), ts)
                            if var_id is not None:
                                timestamp_map[var_id] = max(timestamp_map.get(var_id, 0), ts)

            if self.state['view_scope'] == 'consolidated':
                res.sort(key=lambda x: timestamp_map.get(x.api_card.id, 0), reverse=reverse)
            else:
                res.sort(key=lambda x: timestamp_map.get(x.variant_id, timestamp_map.get(x.api_card.id, 0)), reverse=reverse)

        return res

app = MockApp()
cards = [MockCard(MockApiCard(1)), MockCard(MockApiCard(3)), MockCard(MockApiCard(2)), MockCard(MockApiCard(4))]

print("Consolidated View (Descending)")
app.state['view_scope'] = 'consolidated'
sorted_cards = app.apply_filters(cards.copy())
print([c.api_card.id for c in sorted_cards])

print("Collectors View (Descending)")
app.state['view_scope'] = 'collectors'
cards_col = [MockCard(MockApiCard(1), "var_1"), MockCard(MockApiCard(3), "var_3"), MockCard(MockApiCard(2), "var_2"), MockCard(MockApiCard(4))]
sorted_cards_col = app.apply_filters(cards_col.copy())
print([c.api_card.id for c in sorted_cards_col])
