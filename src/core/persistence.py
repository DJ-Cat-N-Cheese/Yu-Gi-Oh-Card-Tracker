import json
import yaml
import os
import time
import logging
import unicodedata
import uuid
from urllib.parse import unquote
from typing import List, Optional
from src.core.models import Collection, Deck

DATA_DIR = "data"
COLLECTIONS_DIR = os.path.join(DATA_DIR, "collections")
DECKS_DIR = os.path.join(DATA_DIR, "decks")
logger = logging.getLogger(__name__)


def sanitize_collection_filename(filename: str) -> str:
    """Validate and return a collection filename without path components."""
    raw_filename = str(filename or '').strip()

    # Check the raw name plus URL-decoded and Unicode-normalized forms so
    # encoded traversal sequences (%2e%2e%2f, %252e...) and lookalike
    # characters (fullwidth dots/slashes) cannot smuggle path components
    # past the literal checks below.
    candidates = {raw_filename}
    decoded = raw_filename
    for _ in range(3):
        decoded = unquote(decoded)
        candidates.add(decoded)
    for candidate in list(candidates):
        candidates.add(unicodedata.normalize('NFKC', candidate))

    for candidate in candidates:
        if '\0' in candidate:
            raise ValueError('Collection name cannot contain null bytes')
        if any(token in candidate for token in ('/', '\\', '..')):
            raise ValueError("Collection name cannot include path separators or '..'")

    clean_filename = os.path.basename(raw_filename)
    if not clean_filename or clean_filename in {'.', '..'}:
        raise ValueError('Invalid collection name')
    if clean_filename != raw_filename:
        raise ValueError('Collection name cannot include path components')

    return clean_filename


class PersistenceManager:
    def __init__(self, data_dir: str = COLLECTIONS_DIR, decks_dir: str = DECKS_DIR):
        self.data_dir = data_dir
        self.decks_dir = decks_dir
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.decks_dir, exist_ok=True)

    def list_collections(self) -> List[str]:
        """Returns a list of available collection filenames."""
        files = [f for f in os.listdir(self.data_dir) if f.endswith(('.json', '.yaml', '.yml'))]
        return files

    def load_collection(self, filename: str) -> Collection:
        """Loads a collection from a JSON or YAML file."""
        filename = sanitize_collection_filename(filename)
        logger.info(f"Loading collection: {filename}")
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logger.error(f"Collection file {filename} not found.")
            raise FileNotFoundError(f"Collection file {filename} not found.")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    data = json.load(f)
                elif filename.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    raise ValueError("Unsupported file format")

            return Collection(**data)
        except Exception as e:
            logger.error(f"Error loading collection {filename}: {e}")
            raise

    def save_collection(self, collection: Collection, filename: str):
        """Saves a collection to a file."""
        filename = sanitize_collection_filename(filename)
        logger.info(f"Saving collection: {filename}")
        filepath = os.path.join(self.data_dir, filename)
        data = collection.model_dump(mode='json')
        # Use UUID to prevent collisions if multiple saves run concurrently
        temp_filepath = filepath + f".{uuid.uuid4()}.tmp"

        try:
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    json.dump(data, f, indent=2)
                elif filename.endswith(('.yaml', '.yml')):
                    yaml.safe_dump(data, f)
                else:
                    raise ValueError("Unsupported file format")
                f.flush()
                os.fsync(f.fileno())

            # Retry logic for Windows file locking issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    os.replace(temp_filepath, filepath)
                    break
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.1)  # Wait a bit before retrying
                    else:
                        raise e
        except Exception as e:
            logger.error(f"Error saving collection {filename}: {e}")
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass
            raise

    # --- Deck Management ---

    def list_deck_groups(self) -> List[str]:
        """Returns a list of available deck groups (subfolders). 'main' is always included for the root."""
        groups = ['main']
        if os.path.exists(self.decks_dir):
            for item in os.listdir(self.decks_dir):
                item_path = os.path.join(self.decks_dir, item)
                if item != 'main' and os.path.isdir(item_path):
                    groups.append(item)
        return sorted(groups)

    def normalize_deck_group(self, group: str) -> str:
        """Returns a filesystem-safe deck group name."""
        if not group or str(group).lower() == 'main':
            return 'main'

        clean_group = "".join(c for c in str(group) if c.isalnum() or c in " -_").strip()
        if not clean_group:
            raise ValueError("Invalid deck group name")
        return clean_group

    def _sanitize_deck_filename(self, filename: str) -> str:
        """Returns a safe .ydk filename without path components."""
        raw_filename = str(filename or '').strip()
        clean_filename = os.path.basename(raw_filename)
        if not clean_filename or clean_filename in {'.', '..'}:
            raise ValueError("Invalid deck filename")
        if clean_filename != raw_filename:
            raise ValueError("Deck filename cannot include path separators")
        if not clean_filename.lower().endswith('.ydk'):
            raise ValueError("Deck filename must end with .ydk")
        return clean_filename

    def _get_group_dir(self, group: str) -> str:
        """Helper to get the directory for a deck group."""
        clean_group = self.normalize_deck_group(group)
        if clean_group == 'main':
            return self.decks_dir

        group_dir = os.path.join(self.decks_dir, clean_group)
        os.makedirs(group_dir, exist_ok=True)
        return group_dir

    def create_deck_group(self, group: str) -> str:
        """Creates a deck group folder and returns the sanitized group name."""
        clean_group = self.normalize_deck_group(group)
        self._get_group_dir(clean_group)
        return clean_group

    def list_decks(self, group: str = 'main') -> List[str]:
        """Returns a list of available deck filenames in a specific group."""
        group_dir = self._get_group_dir(group)
        if not os.path.exists(group_dir):
            return []
        files = [f for f in os.listdir(group_dir) if f.endswith('.ydk')]
        return files

    def load_deck(self, filename: str, group: str = 'main') -> Deck:
        """Loads a deck from a .ydk file in a specific group."""
        group_dir = self._get_group_dir(group)
        filename = self._sanitize_deck_filename(filename)
        logger.info(f"Loading deck: {filename} from group {group}")
        filepath = os.path.join(group_dir, filename)
        if not os.path.exists(filepath):
            logger.error(f"Deck file {filename} not found.")
            raise FileNotFoundError(f"Deck file {filename} not found.")

        deck = Deck(name=filename.replace('.ydk', ''))
        current_section = 'main'

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    if line.startswith('#'):
                        if 'main' in line.lower():
                            current_section = 'main'
                        elif 'extra' in line.lower():
                            current_section = 'extra'
                        elif 'side' in line.lower():
                            current_section = 'side'
                        continue
                    elif line.startswith('!'):
                        if 'side' in line.lower():
                            current_section = 'side'
                        continue

                    if not line.isdigit():
                        continue

                    card_id = int(line)
                    if current_section == 'main':
                        deck.main.append(card_id)
                    elif current_section == 'extra':
                        deck.extra.append(card_id)
                    elif current_section == 'side':
                        deck.side.append(card_id)

            return deck
        except Exception as e:
            logger.error(f"Error loading deck {filename}: {e}")
            raise

    def save_deck(self, deck: Deck, filename: str, group: str = 'main'):
        """Saves a deck to a .ydk file in a specific group."""
        group_dir = self._get_group_dir(group)
        filename = self._sanitize_deck_filename(filename)
        logger.info(f"Saving deck: {filename} to group {group}")
        filepath = os.path.join(group_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("#created by OpenYugi\n")
                f.write("#main\n")
                for card_id in deck.main:
                    f.write(f"{card_id}\n")

                f.write("#extra\n")
                for card_id in deck.extra:
                    f.write(f"{card_id}\n")

                f.write("!side\n")
                for card_id in deck.side:
                    f.write(f"{card_id}\n")

        except Exception as e:
            logger.error(f"Error saving deck {filename}: {e}")
            raise

    def save_deck_content(self, content: str, filename: str, group: str = 'main'):
        """Saves raw .ydk content to a deck file in a specific group."""
        group_dir = self._get_group_dir(group)
        filename = self._sanitize_deck_filename(filename)
        logger.info(f"Saving imported deck content: {filename} to group {group}")
        filepath = os.path.join(group_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error saving deck content {filename}: {e}")
            raise

    def delete_deck(self, filename: str, group: str = 'main'):
        """Deletes a deck file in a specific group."""
        group_dir = self._get_group_dir(group)
        filename = self._sanitize_deck_filename(filename)
        logger.info(f"Deleting deck: {filename} from group {group}")
        filepath = os.path.join(group_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logger.error(f"Error deleting deck {filename}: {e}")
                raise
        else:
            logger.warning(f"Deck file {filename} not found for deletion.")

    # --- UI State Persistence ---

    def load_ui_state(self) -> dict:
        """Loads UI state from data/ui_state.json."""
        filepath = os.path.join(DATA_DIR, "ui_state.json")
        if not os.path.exists(filepath):
            return {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading UI state: {e}")
            return {}

    def save_ui_state(self, state: dict):
        """Saves UI state to data/ui_state.json. Merges with existing state."""
        filepath = os.path.join(DATA_DIR, "ui_state.json")
        try:
            current = self.load_ui_state()
            current.update(state)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(current, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving UI state: {e}")

# Global instance
persistence = PersistenceManager()
