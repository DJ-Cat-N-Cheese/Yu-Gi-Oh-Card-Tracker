import os
import shutil
from typing import Optional, List
from src.core.models import Collection, StorageContainer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageService:
    def get_storage_image_dir(self, collection_name: str) -> str:
        """
        Returns the directory path for storage images for a specific collection.
        Ensures the directory exists.
        collection_name should be the filename without extension.
        """
        # Sanitization could be improved, but assuming valid filename usage
        safe_name = collection_name.replace('.json', '').replace('.yaml', '')
        base = os.path.join('data', 'collection', 'storage_pictures', safe_name)
        os.makedirs(base, exist_ok=True)
        return base

    def save_storage_image(self, collection_name: str, storage_name: str, temp_file_path: str) -> Optional[str]:
        """
        Moves a temporary file to the storage directory and returns the relative path for the UI.
        """
        if not temp_file_path or not os.path.exists(temp_file_path):
            return None

        directory = self.get_storage_image_dir(collection_name)
        # Determine extension
        _, ext = os.path.splitext(temp_file_path)
        if not ext: ext = '.jpg'

        # Sanitize storage name for filename
        safe_storage_name = "".join(c for c in storage_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        filename = f"{safe_storage_name}{ext}"
        dest_path = os.path.join(directory, filename)

        try:
            shutil.copy2(temp_file_path, dest_path)
            # Return path relative to data/ ? Or absolute?
            # The UI usually serves static files.
            # If we want to serve this via a static route, we need to know how NiceGUI serves 'data'.
            # Usually we might need a custom route or serve /data.
            # For now, let's return the relative path from project root.
            return dest_path
        except Exception as e:
            logger.error(f"Failed to save storage image: {e}")
            return None

    def add_storage(self, collection: Collection, name: str, type: str, description: str = "", image_path: str = None) -> StorageContainer:
        """
        Adds a new storage container to the collection.
        """
        if any(s.name == name for s in collection.storage):
            raise ValueError(f"Storage '{name}' already exists.")

        container = StorageContainer(
            name=name,
            type=type,
            description=description,
            image_path=image_path,
            creation_date=datetime.now().isoformat()
        )
        collection.storage.append(container)
        return container

    def update_storage(self, collection: Collection, old_name: str, new_name: str, type: str, description: str, image_path: str = None):
        """
        Updates an existing storage container. Handles renaming references if name changes.
        """
        container = next((s for s in collection.storage if s.name == old_name), None)
        if not container:
             raise ValueError("Storage not found")

        # Check uniqueness if name changed
        if new_name != old_name:
             if any(s.name == new_name for s in collection.storage):
                 raise ValueError(f"Storage '{new_name}' already exists.")

        container.name = new_name
        container.type = type
        container.description = description
        if image_path:
            container.image_path = image_path

        # If name changed, update all cards!
        if new_name != old_name:
             self._update_card_references(collection, old_name, new_name)

    def _update_card_references(self, collection: Collection, old_name: str, new_name: Optional[str]):
        """
        Updates storage_location for all entries matching old_name to new_name.
        Merges entries if target location already exists for the same card attributes.
        """
        for card in collection.cards:
            for variant in card.variants:
                entries_to_remove = []

                # Find all entries that need moving
                moving_entries = [e for e in variant.entries if e.storage_location == old_name]

                for entry in moving_entries:
                    # Check if there is ALREADY an entry with new_name and same attrs
                    target_entry = next((e for e in variant.entries
                                         if e.storage_location == new_name and
                                            e.condition == entry.condition and
                                            e.language == entry.language and
                                            e.first_edition == entry.first_edition and
                                            e is not entry), None)

                    if target_entry:
                        # Merge
                        target_entry.quantity += entry.quantity
                        entries_to_remove.append(entry)
                    else:
                        # Update
                        entry.storage_location = new_name

                # Cleanup merged entries
                for e in entries_to_remove:
                    if e in variant.entries:
                        variant.entries.remove(e)

    def delete_storage(self, collection: Collection, name: str):
        """
        Deletes a storage container and moves its contents to 'None' (loose).
        """
        # Move all cards in this storage to None (Loose)
        self._update_card_references(collection, name, None)

        collection.storage = [s for s in collection.storage if s.name != name]

storage_service = StorageService()
