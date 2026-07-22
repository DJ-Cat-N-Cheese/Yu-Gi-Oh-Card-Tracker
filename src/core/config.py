import json
import os
import stat
import tempfile
import threading
from typing import Dict, Any

from werkzeug.security import generate_password_hash

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self._lock = threading.RLock()
        self.config: Dict[str, Any] = self._load_config()
        self._ensure_auth_config()

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
            "collection_show_unique_cards": True,
            "collection_show_unique_variants": True,
            "collection_show_total_qty": True,
            "collection_show_rarity_breakdown": True,
            "collection_show_language_breakdown": True,
            "collection_show_price_preview": False
        }

    def save_config(self):
        """Persist config atomically and restrict it to the current OS user."""
        with self._lock:
            directory = os.path.dirname(os.path.abspath(self.config_file))
            os.makedirs(directory, exist_ok=True)
            fd, temporary_path = tempfile.mkstemp(prefix='.openyugi-config-', dir=directory)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as file:
                    json.dump(self.config, file, indent=2)
                    file.flush()
                    os.fsync(file.fileno())
                os.chmod(temporary_path, stat.S_IRUSR | stat.S_IWUSR)
                os.replace(temporary_path, self.config_file)
            finally:
                if os.path.exists(temporary_path):
                    os.remove(temporary_path)

    def _ensure_auth_config(self) -> None:
        """Migrate existing configs to secure, hashed default credentials."""
        changed = False
        if not isinstance(self.config.get("auth_username"), str):
            self.config["auth_username"] = "admin"
            changed = True
        if not isinstance(self.config.get("auth_password_hash"), str):
            self.config["auth_password_hash"] = generate_password_hash("admin", method="scrypt")
            changed = True
        if changed:
            self.save_config()
        if os.path.exists(self.config_file):
            os.chmod(self.config_file, stat.S_IRUSR | stat.S_IWUSR)

    def get_auth_username(self) -> str:
        env_username = os.environ.get("OPENYUGI_ADMIN_USERNAME")
        if env_username:
            return env_username
        return self.config["auth_username"]

    def get_auth_password_hash(self) -> str:
        env_password_hash = os.environ.get("OPENYUGI_ADMIN_PASSWORD_HASH")
        if env_password_hash:
            return env_password_hash
        return self.config["auth_password_hash"]

    def set_auth_credentials(self, username: str, password_hash: str) -> None:
        with self._lock:
            self.config["auth_username"] = username
            self.config["auth_password_hash"] = password_hash
            self.save_config()

    def set_application_settings(
        self,
        language: str,
        deck_builder_page_size: int,
        bulk_add_page_size: int,
    ) -> None:
        with self._lock:
            self.config["language"] = language
            self.config["deck_builder_page_size"] = deck_builder_page_size
            self.config["bulk_add_page_size"] = bulk_add_page_size
            self.save_config()

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
        # Handle backwards compatibility for 'unique_counts'
        unique_cards = self.config.get("collection_show_unique_cards", self.config.get("collection_show_unique_counts", True))
        unique_variants = self.config.get("collection_show_unique_variants", self.config.get("collection_show_unique_counts", True))

        return {
            "total_value": self.config.get("collection_show_total_value", True),
            "unique_cards": unique_cards,
            "unique_variants": unique_variants,
            "total_qty": self.config.get("collection_show_total_qty", True),
            "rarity_breakdown": self.config.get("collection_show_rarity_breakdown", True),
            "language_breakdown": self.config.get("collection_show_language_breakdown", True),
            "price_preview": self.config.get("collection_show_price_preview", False)
        }

    def set_collection_metrics_config(self, key: str, value: bool):
        valid_keys = {
            "total_value": "collection_show_total_value",
            "unique_cards": "collection_show_unique_cards",
            "unique_variants": "collection_show_unique_variants",
            "total_qty": "collection_show_total_qty",
            "rarity_breakdown": "collection_show_rarity_breakdown",
            "language_breakdown": "collection_show_language_breakdown",
            "price_preview": "collection_show_price_preview"
        }
        if key in valid_keys:
            self.config[valid_keys[key]] = value
            self.save_config()

config_manager = ConfigManager()
