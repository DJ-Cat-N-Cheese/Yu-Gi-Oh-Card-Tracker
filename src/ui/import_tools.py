from nicegui import ui, events
import json
import logging
from typing import Optional, List, Dict, Any
import asyncio

from src.core.persistence import persistence
from src.core.models import Collection
from src.services.ygo_api import ygo_service
from src.services.collection_editor import CollectionEditor

logger = logging.getLogger(__name__)

class ImportController:
    def __init__(self):
        self.collections: List[str] = []
        self.selected_collection: Optional[str] = None
        self.import_mode: str = 'ADD'
        self.undo_stack: List[Dict[str, Any]] = []

        self.collection_select = None
        self.undo_button = None

        self.refresh_collections()

    def refresh_collections(self):
        self.collections = persistence.list_collections()
        if self.collection_select:
            self.collection_select.options = self.collections
            self.collection_select.update()

    async def create_new_collection(self, name: str):
        if not name:
            ui.notify("Collection name cannot be empty", type='warning')
            return

        filename = f"{name}.json"
        if filename in self.collections:
             ui.notify("Collection already exists", type='negative')
             return

        new_collection = Collection(name=name)
        persistence.save_collection(new_collection, filename)

        self.refresh_collections()
        self.selected_collection = filename
        if self.collection_select:
            self.collection_select.value = filename
            self.collection_select.update()

        ui.notify(f"Created collection: {name}", type='positive')

    async def handle_import(self, e: events.UploadEventArguments):
        if not self.selected_collection:
            ui.notify("Please select a collection first", type='warning')
            return

        try:
            content = e.content.read()
            if asyncio.iscoroutine(content):
                content = await content

            logger.info(f"File content read: {len(content)} bytes")
            json_str = content.decode('utf-8')
            data = json.loads(json_str)
        except Exception as ex:
            ui.notify(f"Invalid JSON: {ex}", type='negative')
            return

        if "cards" not in data:
            ui.notify("Invalid JSON format: missing 'cards' list", type='negative')
            return

        # Load target collection
        try:
            collection = persistence.load_collection(self.selected_collection)
        except Exception as ex:
            ui.notify(f"Error loading collection: {ex}", type='negative')
            return

        # Save state for undo (deep copy via model_dump)
        self.undo_stack.append({
            "filename": self.selected_collection,
            "data": collection.model_dump(mode='json')
        })

        if self.undo_button:
            self.undo_button.visible = True
            self.undo_button.update()

        # Process
        changes_count = 0

        # Ensure DB is loaded for lookups
        logger.info("Loading card database...")
        await ygo_service.load_card_database()
        logger.info("Card database loaded.")

        for card_data in data.get("cards", []):
            card_id = card_data.get("card_id")
            if not card_id:
                continue

            api_card = ygo_service.get_card(card_id)
            if not api_card:
                logger.warning(f"Card {card_id} not found in database. Skipping.")
                continue

            # Default image ID if needed
            default_image_id = api_card.card_images[0].id if api_card.card_images else None

            for variant_data in card_data.get("variants", []):
                set_code = variant_data.get("set_code")
                rarity = variant_data.get("rarity")
                image_id = variant_data.get("image_id", default_image_id)

                if not set_code or not rarity:
                    continue

                for entry_data in variant_data.get("entries", []):
                    quantity = entry_data.get("quantity", 0)
                    condition = entry_data.get("condition", "Near Mint")
                    language = entry_data.get("language", "EN")
                    first_edition = entry_data.get("first_edition", False)

                    if quantity <= 0:
                        continue

                    # Adjust quantity for subtract mode
                    final_qty_change = quantity if self.import_mode == 'ADD' else -quantity

                    # Use CollectionEditor
                    modified = CollectionEditor.apply_change(
                        collection=collection,
                        api_card=api_card,
                        set_code=set_code,
                        rarity=rarity,
                        language=language,
                        quantity=final_qty_change,
                        condition=condition,
                        first_edition=first_edition,
                        image_id=image_id,
                        mode='ADD'
                    )

                    if modified:
                        changes_count += 1

        if changes_count > 0:
            persistence.save_collection(collection, self.selected_collection)
            ui.notify(f"Import successful. Processed {changes_count} updates.", type='positive')
        else:
            ui.notify("No changes applied.", type='info')

    def undo_last(self):
        if not self.undo_stack:
            return

        state = self.undo_stack.pop()
        filename = state['filename']
        data = state['data']

        try:
            # Restore
            collection = Collection(**data)
            persistence.save_collection(collection, filename)
            ui.notify(f"Undid last import for {filename}", type='positive')

            if not self.undo_stack:
                if self.undo_button:
                    self.undo_button.visible = False
                    self.undo_button.update()

        except Exception as e:
            ui.notify(f"Error undoing: {e}", type='negative')


class MergeController:
    def __init__(self):
        self.collections: List[str] = []
        self.coll_a: Optional[str] = None
        self.coll_b: Optional[str] = None
        self.new_name: str = ""
        self.refresh_collections()

    def refresh_collections(self):
        self.collections = persistence.list_collections()

    async def handle_merge(self):
        # Validate inputs
        if not self.coll_a or not self.coll_b:
            ui.notify("Please select two collections to merge.", type='warning')
            return

        if self.coll_a == self.coll_b:
            ui.notify("Cannot merge a collection into itself.", type='warning')
            return

        if not self.new_name.strip():
            ui.notify("Please enter a name for the new collection.", type='warning')
            return

        new_filename = f"{self.new_name.strip()}.json"
        if new_filename in self.collections:
            ui.notify(f"A collection named '{self.new_name}' already exists.", type='negative')
            return

        ui.notify("Starting merge process...", type='info')

        try:
            # Load Collections
            coll_a_obj = persistence.load_collection(self.coll_a)
            coll_b_obj = persistence.load_collection(self.coll_b)

            # Create New Collection
            new_collection = Collection(name=self.new_name.strip())

            # Ensure DB is loaded
            await ygo_service.load_card_database()

            # Helper function to merge a collection into the new one
            async def merge_into_new(source_coll: Collection):
                for card in source_coll.cards:
                    # We need the ApiCard for CollectionEditor
                    api_card = ygo_service.get_card(card.card_id)
                    if not api_card:
                         # Attempt to construct minimal ApiCard if missing from DB (should verify if this is safe)
                         # Fallback: create mock ApiCard if real one missing?
                         # Better to skip or log warning.
                         logger.warning(f"Card {card.card_id} not found in DB during merge. Skipping.")
                         continue

                    for variant in card.variants:
                        for entry in variant.entries:
                            CollectionEditor.apply_change(
                                collection=new_collection,
                                api_card=api_card,
                                set_code=variant.set_code,
                                rarity=variant.rarity,
                                language=entry.language,
                                quantity=entry.quantity,
                                condition=entry.condition,
                                first_edition=entry.first_edition,
                                image_id=variant.image_id,
                                mode='ADD'
                            )

            # Merge A
            await merge_into_new(coll_a_obj)
            # Merge B
            await merge_into_new(coll_b_obj)

            # Save
            persistence.save_collection(new_collection, new_filename)

            ui.notify(f"Successfully created '{self.new_name}' with merged data.", type='positive')

            # Refresh lists
            self.refresh_collections()
            self.new_name = "" # Reset input

        except Exception as e:
            logger.error(f"Merge failed: {e}")
            ui.notify(f"Merge failed: {e}", type='negative')


def import_tools_page():
    controller = ImportController()
    merge_controller = MergeController()

    with ui.column().classes('w-full q-pa-md gap-4'):
        ui.label('Import Tools').classes('text-h4 q-mb-md')

        # Top Bar: Collection Selection (for Import)
        with ui.card().classes('w-full bg-dark border border-gray-700 p-4'):
             ui.label('Select Target for Import').classes('text-subtitle2 text-grey-4 q-mb-sm')
             with ui.row().classes('w-full items-center gap-4'):
                controller.collection_select = ui.select(
                    options=controller.collections,
                    label="Target Collection",
                    value=controller.selected_collection,
                    on_change=lambda e: setattr(controller, 'selected_collection', e.value)
                ).classes('w-64').props('dark')

                def open_new_collection_dialog():
                    with ui.dialog() as dialog, ui.card().classes('bg-dark border border-gray-700'):
                        ui.label('New Collection Name').classes('text-h6')
                        name_input = ui.input(placeholder='Collection Name').props('dark autofocus')
                        with ui.row().classes('w-full justify-end q-mt-md'):
                             ui.button('Cancel', on_click=dialog.close).props('flat color=grey')

                             async def create_click():
                                 await controller.create_new_collection(name_input.value)
                                 # Refresh merge controller list too
                                 merge_controller.refresh_collections()
                                 # We need to refresh the selects in merge section if they exist,
                                 # but nicegui requires binding or explicit update.
                                 # Since UI is static here, user might need to reload or we make it reactive.
                                 # For simplicty, page reload is fine or just accept it updates on next visit.
                                 dialog.close()

                             ui.button('Create', on_click=create_click).classes('bg-accent text-dark')
                    dialog.open()

                ui.button('New Collection', on_click=open_new_collection_dialog, icon='add').classes('bg-secondary text-dark')

        # Import Section
        with ui.card().classes('w-full bg-dark border border-gray-700 p-6'):
            ui.label('JSON Import').classes('text-xl font-bold q-mb-md')

            with ui.row().classes('items-center gap-6 q-mb-md'):
                ui.label('Mode:').classes('text-lg')
                with ui.row():
                    ui.radio(['ADD', 'SUBTRACT'], value='ADD', on_change=lambda e: setattr(controller, 'import_mode', e.value)).props('dark inline')

            ui.upload(label='Drop JSON here', auto_upload=True, on_upload=controller.handle_import).props('dark accept=.json').classes('w-full')

            # Undo Button (Initially Hidden)
            controller.undo_button = ui.button('Undo Last Import', on_click=controller.undo_last, icon='undo') \
                .classes('bg-red-500 text-white q-mt-md').props('flat')
            controller.undo_button.visible = False

        # Merge Section
        with ui.card().classes('w-full bg-dark border border-gray-700 p-6 q-mt-md'):
            ui.label('Merge Collections').classes('text-xl font-bold q-mb-md')
            ui.label('Combine two collections into a new one. Quantities will be summed. Original collections remain unchanged.').classes('text-sm text-grey-4 q-mb-md')

            with ui.grid().classes('grid-cols-1 md:grid-cols-3 gap-4 w-full items-start'):
                # Collection A
                ui.select(
                    options=merge_controller.collections,
                    label="Collection A",
                    on_change=lambda e: setattr(merge_controller, 'coll_a', e.value)
                ).props('dark').classes('w-full')

                # Collection B
                ui.select(
                    options=merge_controller.collections,
                    label="Collection B",
                    on_change=lambda e: setattr(merge_controller, 'coll_b', e.value)
                ).props('dark').classes('w-full')

                # New Name
                ui.input(
                    label="New Collection Name",
                    placeholder="e.g. Master Collection",
                    on_change=lambda e: setattr(merge_controller, 'new_name', e.value)
                ).props('dark').classes('w-full')

            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('Merge Collections', on_click=merge_controller.handle_merge, icon='merge_type').classes('bg-primary text-white')
