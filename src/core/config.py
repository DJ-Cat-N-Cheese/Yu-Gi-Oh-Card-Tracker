import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_file):
            return self._default_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "language": "en",
            "theme": "dark",
            "deck_builder_page_size": 9,
            "bulk_add_page_size": 50,
            "collection_show_total_value": True,
            "collection_show_unique_counts": True,
            "collection_show_rarity_breakdown": True,
            "collection_show_language_breakdown": True,
            "collection_show_price_preview": False
        }

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def get_language(self) -> str:
        return self.config.get("language", "en")

    def set_language(self, language: str):
        self.config["language"] = language
        self.save_config()

    def get_deck_builder_page_size(self) -> int:
        return self.config.get("deck_builder_page_size", 9)

    def set_deck_builder_page_size(self, size: int):
        self.config["deck_builder_page_size"] = size
        self.save_config()

    def get_bulk_add_page_size(self) -> int:
        return self.config.get("bulk_add_page_size", 50)

    def set_bulk_add_page_size(self, size: int):
        self.config["bulk_add_page_size"] = size
        self.save_config()

    def get_collection_metrics_config(self) -> Dict[str, bool]:
        return {
            "total_value": self.config.get("collection_show_total_value", True),
            "unique_counts": self.config.get("collection_show_unique_counts", True),
            "rarity_breakdown": self.config.get("collection_show_rarity_breakdown", True),
            "language_breakdown": self.config.get("collection_show_language_breakdown", True),
            "price_preview": self.config.get("collection_show_price_preview", False)
        }

    def set_collection_metrics_config(self, key: str, value: bool):
        valid_keys = {
            "total_value": "collection_show_total_value",
            "unique_counts": "collection_show_unique_counts",
            "rarity_breakdown": "collection_show_rarity_breakdown",
            "language_breakdown": "collection_show_language_breakdown",
            "price_preview": "collection_show_price_preview"
        }
        if key in valid_keys:
            self.config[valid_keys[key]] = value
            self.save_config()

config_manager = ConfigManager()
