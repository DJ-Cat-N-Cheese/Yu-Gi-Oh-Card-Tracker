import os
import json
import logging
import shutil
from typing import List, Optional, Dict, Any
from nicegui import run

DATA_DIR = os.path.join(os.getcwd(), "data")
STORAGE_FILE = os.path.join(DATA_DIR, "storage.json")
STORAGE_IMG_DIR = os.path.join(DATA_DIR, "storage")

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self._storage_cache: List[Dict[str, Any]] = []
        self._ensure_dirs()
        self.load_storage_list()

    def _ensure_dirs(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(STORAGE_IMG_DIR, exist_ok=True)

    def load_storage_list(self) -> List[Dict[str, Any]]:
        if not os.path.exists(STORAGE_FILE):
            self._storage_cache = []
            return []

        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                self._storage_cache = json.load(f)
        except Exception as e:
            logger.error(f"Error loading storage list: {e}")
            self._storage_cache = []

        return self._storage_cache

    def save_storage_list(self):
        try:
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._storage_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving storage list: {e}")

    def get_all_storage(self) -> List[Dict[str, Any]]:
        return self._storage_cache

    def get_storage(self, name: str) -> Optional[Dict[str, Any]]:
        for s in self._storage_cache:
            if s['name'] == name:
                return s
        return None

    def add_storage(self, name: str, type_name: str, description: str = "", image_path: str = None, set_code: str = None) -> bool:
        if self.get_storage(name):
            return False # Exists

        new_storage = {
            "name": name,
            "type": type_name,
            "description": description,
            "image_path": image_path,
            "set_code": set_code
        }
        self._storage_cache.append(new_storage)
        self.save_storage_list()
        return True

    def update_storage(self, old_name: str, new_name: str, type_name: str, description: str, image_path: str, set_code: str) -> bool:
        s = self.get_storage(old_name)
        if not s:
            return False

        # If renaming, check conflict
        if old_name != new_name and self.get_storage(new_name):
            return False

        s['name'] = new_name
        s['type'] = type_name
        s['description'] = description
        s['image_path'] = image_path
        s['set_code'] = set_code

        self.save_storage_list()
        return True

    def delete_storage(self, name: str) -> bool:
        s = self.get_storage(name)
        if not s:
            return False

        self._storage_cache.remove(s)
        self.save_storage_list()

        # Cleanup image if custom
        if s.get('image_path') and os.path.exists(s['image_path']):
            # Only delete if it is in our storage folder (safety check)
            if STORAGE_IMG_DIR in os.path.abspath(s['image_path']):
                try:
                    os.remove(s['image_path'])
                except:
                    pass

        return True

    async def save_uploaded_image(self, file, filename: str) -> str:
        """
        Saves an uploaded file to data/storage/ and returns the relative path or web path.
        Returns the filename relative to serving root if needed, or absolute path.
        We will store absolute path in JSON but UI usually needs /storage/filename.
        Actually, let's store just the filename in JSON if it's in data/storage.
        """
        # Clean filename
        safe_name = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.')).strip()
        file_path = os.path.join(STORAGE_IMG_DIR, safe_name)

        try:
            # If it's a NiceGUI UploadFile (SpooledTemporaryFile)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            return safe_name
        except Exception as e:
            logger.error(f"Error saving storage image: {e}")
            return None

storage_service = StorageService()
