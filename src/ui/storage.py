from nicegui import ui, run, events
from src.core.models import Collection, StorageContainer, CollectionEntry
from src.core.persistence import persistence
from src.services.storage_service import storage_service
from src.services.ygo_api import ygo_service
from src.services.collection_editor import CollectionEditor
from src.services.image_manager import image_manager
from src.ui.components.filter_pane import FilterPane
from src.ui.components.single_card_view import SingleCardView
from src.core.utils import LANGUAGE_COUNTRY_MAP, generate_variant_id
import logging
import asyncio
from typing import Optional, List, Dict
import traceback

logger = logging.getLogger(__name__)

class StoragePage:
    def __init__(self):
        self.state = {
            'view': 'gallery', # gallery, detail
            'current_collection': None, # Collection object
            'selected_collection_file': None,
            'selected_storage': None, # StorageContainer object

            # Detail View State
            'in_storage_view': False, # False = Showing Loose cards, True = Showing content of storage
            'filtered_cards': [], # List of row objects
            'page': 1,
            'page_size': 48,
            'total_pages': 1,

            # Filters (reusing same structure as CollectionPage for FilterPane compatibility)
            'search_text': '',
            'filter_set': '',
            'filter_rarity': '',
            'filter_attr': '',
            'filter_card_type': ['Monster', 'Spell', 'Trap'],
            'filter_condition': [],
            'filter_monster_race': '',
            'filter_st_race': '',
            'filter_archetype': '',
            'filter_monster_category': [],
            'filter_level': None,
            'filter_atk_min': 0,
            'filter_atk_max': 5000,
            'filter_def_min': 0,
            'filter_def_max': 5000,
            'filter_ownership_min': 0,
            'filter_ownership_max': 100,
            'filter_price_min': 0.0,
            'filter_price_max': 1000.0,
            'filter_owned_lang': '',

            # Options
            'available_sets': [],
            'available_monster_races': [],
            'available_st_races': [],
            'available_archetypes': [],
            'available_card_types': ['Monster', 'Spell', 'Trap', 'Skill'],
            'max_owned_quantity': 100,

            'sort_by': 'Name',
            'sort_descending': False,
        }

        # Load initial collection selection from persistence
        files = persistence.list_collections()
        saved_state = persistence.load_ui_state()
        saved_file = saved_state.get('last_collection') # Sharing with Browse Sets logic or separate? Let's use last_collection.

        if saved_file and saved_file in files:
            self.state['selected_collection_file'] = saved_file
        elif files:
            self.state['selected_collection_file'] = files[0]

        self.filter_pane = None
        self.single_card_view = SingleCardView()
        self.api_card_map = {}

    async def load_data(self):
        # Load Collection
        if self.state['selected_collection_file']:
            try:
                self.state['current_collection'] = await run.io_bound(persistence.load_collection, self.state['selected_collection_file'])
            except Exception as e:
                logger.error(f"Error loading collection: {e}")
                ui.notify(f"Error loading collection: {e}", type='negative')

        # Load API Database for Filters/Details
        lang_code = 'en' # Simplified for now, or use config
        try:
            api_cards = await ygo_service.load_card_database(lang_code)
            self.api_card_map = {c.id: c for c in api_cards}

            # Populate Filters Options
            sets = set()
            m_races = set()
            st_races = set()
            archetypes = set()

            for c in api_cards:
                if c.card_sets:
                    for s in c.card_sets:
                        parts = s.set_code.split('-')
                        prefix = parts[0] if len(parts) > 0 else s.set_code
                        sets.add(f"{s.set_name} | {prefix}")
                if c.archetype: archetypes.add(c.archetype)
                if "Monster" in c.type: m_races.add(c.race)
                elif "Spell" in c.type or "Trap" in c.type:
                    if c.race: st_races.add(c.race)

            self.state['available_sets'] = sorted(list(sets))
            self.state['available_monster_races'] = sorted(list(m_races))
            self.state['available_st_races'] = sorted(list(st_races))
            self.state['available_archetypes'] = sorted(list(archetypes))

        except Exception as e:
            logger.error(f"Error loading API DB: {e}")

        if self.filter_pane:
            self.filter_pane.update_options()

        if self.state['view'] == 'gallery':
            self.render_gallery.refresh()
        else:
            await self.apply_detail_filters()

    async def open_storage_dialog(self, storage: Optional[StorageContainer] = None):
        is_edit = storage is not None

        # Dialog State
        d_state = {
            'name': storage.name if storage else '',
            'type': storage.type if storage else 'Box',
            'description': storage.description if storage else '',
            'image_path': storage.image_path if storage else None,
            'sealed_set': None,
            'temp_image': None # For uploads
        }

        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            ui.label('Edit Storage' if is_edit else 'New Storage').classes('text-h6')

            # Type Selection
            ui.select(['Box', 'Binder', 'Sealed Product'], label='Type', value=d_state['type']).bind_value(d_state, 'type').classes('w-full')

            # Sealed Product Set Selector (Visible only if Sealed Product)
            sealed_container = ui.column().classes('w-full hidden')

            async def load_sets():
                sets = await ygo_service.get_all_sets_info()
                options = {s['code']: f"{s['name']} ({s['code']})" for s in sets}

                def on_set_change(e):
                    if not e.value: return
                    code = e.value
                    info = next((s for s in sets if s['code'] == code), None)
                    if info:
                        # Prefill name if empty or default
                        if not d_state['name'] or 'Box' in d_state['name']:
                             # "[product name]-box"
                             d_state['name'] = f"{info['name']} Box"
                             name_input.value = d_state['name'] # Update UI

                        # Prefill image
                        if info.get('image'):
                             d_state['image_path'] = info['image'] # Use URL directly? Or download?
                             # Requirement says: "saved as described above". So we should download it.
                             img_preview.set_source(info['image'])

                ui.select(options, label='Select Set', with_input=True, on_change=on_set_change).classes('w-full')

            ui.timer(0.1, load_sets, once=True)

            def on_type_change(e):
                if e.value == 'Sealed Product':
                    sealed_container.classes(remove='hidden')
                else:
                    sealed_container.classes(add='hidden')
                d_state['type'] = e.value

            # Re-bind logic for visibility
            # Since ui.select doesn't trigger on_change for initial bind, check manually or use visibility binding
            # Let's just use a reactive refresh or standard visibility binding?
            # Creating a fresh select for the bind call

            # Name Input
            name_input = ui.input('Name').bind_value(d_state, 'name').classes('w-full')

            # Description
            ui.textarea('Description').bind_value(d_state, 'description').classes('w-full')

            # Image Upload
            ui.label('Image').classes('text-sm text-gray-400 mt-2')
            img_preview = ui.image(d_state['image_path'] or 'https://placehold.co/400x300?text=No+Image').classes('w-full h-48 object-contain bg-black/10 rounded mb-2')

            def handle_upload(e: events.UploadEventArguments):
                # Save to temp?
                # NiceGUI upload keeps in memory usually?
                # We need to save content.
                # Use a temp dir
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(e.name)[1]) as tmp:
                    tmp.write(e.content.read())
                    d_state['temp_image'] = tmp.name
                    img_preview.set_source(f"/_nicegui/auto/static/{tmp.name}") # Hacky? No, just set source to local path if allowed?
                    # UI.image doesn't serve arbitrary local files easily without route.
                    # But for preview we can use base64?
                    # Let's stick to saving logic later. For preview, maybe base64 is safer.
                    pass

                # Base64 for preview
                import base64
                e.content.seek(0)
                b64 = base64.b64encode(e.content.read()).decode('utf-8')
                img_preview.set_source(f"data:image/{os.path.splitext(e.name)[1][1:]};base64,{b64}")

            ui.upload(on_upload=handle_upload, auto_upload=True).classes('w-full')

            # Render sealed container inside the flow
            with sealed_container:
                 pass # Already populated above, just placing it in context

            # Trigger visibility check
            # We need to reconstruct or bind classes.
            # Simple approach: Check on open.
            if d_state['type'] == 'Sealed Product':
                sealed_container.classes(remove='hidden')

            # We need to attach the listener to the TYPE select.
            # But I created it earlier.
            # I'll create a new one here properly.

        # Re-doing the layout slightly to ensure correct order
        dialog.close()
        dialog = ui.dialog()
        with dialog, ui.card().classes('w-[500px]'):
            ui.label('Edit Storage' if is_edit else 'New Storage').classes('text-h6')

            sealed_section = ui.column().classes('w-full hidden')

            def type_changed(e):
                d_state['type'] = e.value
                if e.value == 'Sealed Product':
                    sealed_section.classes(remove='hidden')
                else:
                    sealed_section.classes(add='hidden')

            ui.select(['Box', 'Binder', 'Sealed Product'], label='Type', value=d_state['type'], on_change=type_changed).classes('w-full')

            # Sealed Section Content
            with sealed_section:
                async def load_sets_dropdown():
                     sets_info = await ygo_service.get_all_sets_info()
                     # Sort by date desc
                     sets_info.sort(key=lambda x: x.get('date') or '', reverse=True)

                     opts = {s['code']: f"{s['name']} ({s['code']})" for s in sets_info}

                     def on_set_select(e):
                         if not e.value: return
                         code = e.value
                         d_state['sealed_set'] = code
                         info = next((s for s in sets_info if s['code'] == code), None)
                         if info:
                             if not d_state['name'] or 'Box' in d_state['name']:
                                  d_state['name'] = f"{info['name']} Box"
                                  name_input.value = d_state['name']

                             if info.get('image'):
                                 d_state['image_path'] = info['image'] # Mark as URL
                                 img_preview.set_source(info['image'])
                                 # We will download on save

                     ui.select(opts, label='Select Set', with_input=True, on_change=on_set_select).classes('w-full')

                # Load immediately
                ui.timer(0.01, load_sets_dropdown, once=True)

            if d_state['type'] == 'Sealed Product':
                sealed_section.classes(remove='hidden')

            name_input = ui.input('Name').bind_value(d_state, 'name').classes('w-full')
            ui.textarea('Description').bind_value(d_state, 'description').classes('w-full')

            ui.label('Image').classes('text-sm text-gray-400 mt-2')
            img_src = d_state['image_path']
            # If path is local relative, prepend /storage/... wait, we need a route.
            # Or use raw path if we map it.
            # Let's assume absolute URL or we will fix serving later.
            # If it's a file path from our storage, it needs a static route.
            # Plan step 6 said: "Save storage pictures in data/collection/storage_pictures/[collection_name]/".
            # "The application serves user-uploaded storage images from the data/storage directory via the /storage static route."
            # Wait, memory said: "The application serves user-uploaded storage images from the data/storage directory via the /storage static route."
            # But I am saving to `data/collection/storage_pictures/...`.
            # I should probably map `/storage_images` to `data/collection/storage_pictures`.
            # I will add this assumption to "Integration" step or handle it here.
            # For now, let's try to display whatever we have.

            img_preview = ui.image(img_src or 'https://placehold.co/400x300?text=No+Image').classes('w-full h-48 object-contain bg-black/10 rounded mb-2')

            def handle_upload(e: events.UploadEventArguments):
                import tempfile
                import base64
                # Save to temp file for processing later
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(e.name)[1]) as tmp:
                    tmp.write(e.content.read())
                    d_state['temp_image'] = tmp.name

                # Preview
                e.content.seek(0)
                b64 = base64.b64encode(e.content.read()).decode('utf-8')
                img_preview.set_source(f"data:image/{os.path.splitext(e.name)[1][1:]};base64,{b64}")
                d_state['image_path'] = None # Clear old path so we know to use temp

            ui.upload(on_upload=handle_upload, auto_upload=True).classes('w-full')

            async def save():
                if not d_state['name']:
                    ui.notify("Name is required", type='warning')
                    return

                col = self.state['current_collection']

                # Image Handling
                final_image_path = d_state['image_path']

                # 1. If we have a temp upload
                col_filename = self.state['selected_collection_file']
                col_name_safe = col_filename.replace('.json', '').replace('.yaml', '').replace('.yml', '')

                if d_state['temp_image']:
                    final_image_path = storage_service.save_storage_image(col_name_safe, d_state['name'], d_state['temp_image'])
                    os.unlink(d_state['temp_image'])

                # 2. If it is a URL (from Sealed Set) and NOT a local path
                elif final_image_path and final_image_path.startswith('http'):
                    # Download it
                    import requests
                    import tempfile
                    try:
                        r = await run.io_bound(requests.get, final_image_path)
                        if r.status_code == 200:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                                tmp.write(r.content)
                                tmp_name = tmp.name

                            final_image_path = storage_service.save_storage_image(col_name_safe, d_state['name'], tmp_name)
                            os.unlink(tmp_name)
                    except Exception as e:
                        logger.error(f"Failed to download sealed image: {e}")
                        # Fallback to URL? No, requirement says save it.
                        pass

                try:
                    if is_edit:
                        storage_service.update_storage(col, storage.name, d_state['name'], d_state['type'], d_state['description'], final_image_path)
                        ui.notify(f"Updated {d_state['name']}")
                    else:
                        storage_service.add_storage(col, d_state['name'], d_state['type'], d_state['description'], final_image_path)
                        ui.notify(f"Created {d_state['name']}")

                    await run.io_bound(persistence.save_collection, col, self.state['selected_collection_file'])
                    dialog.close()
                    await self.load_data()
                except ValueError as e:
                    ui.notify(str(e), type='negative')
                except Exception as e:
                    logger.error(f"Error saving storage: {e}")
                    ui.notify(f"Error: {e}", type='negative')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=save).props('color=primary')

        dialog.open()

    @ui.refreshable
    def render_gallery(self):
        col = self.state['current_collection']
        if not col:
            ui.label('No Collection Selected').classes('text-white')
            return

        # Header with "New Storage"
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('Storage Containers').classes('text-h5 text-white')
            ui.button('New Storage', icon='add', on_click=lambda: self.open_storage_dialog(None)).props('color=positive')

        if not col.storage:
            ui.label("No storage containers yet. Create one!").classes('text-gray-400 italic')
            return

        with ui.grid(columns='repeat(auto-fill, minmax(250px, 1fr))').classes('w-full gap-4'):
            for s in col.storage:
                self.render_storage_card(s)

    def render_storage_card(self, storage: StorageContainer):
        # Calculate stats
        # Total Cards, Value
        count = 0
        value = 0.0

        if self.state['current_collection']:
             for c in self.state['current_collection'].cards:
                 for v in c.variants:
                     for e in v.entries:
                         if e.storage_location == storage.name:
                             count += e.quantity
                             value += (e.market_value or 0.0) * e.quantity

        with ui.card().classes('w-full p-0 cursor-pointer hover:scale-105 transition-transform bg-gray-900 border border-gray-700') \
                      .on('click', lambda: self.open_detail_view(storage)):

             # Image
             img_path = storage.image_path
             if img_path and not img_path.startswith('http'):
                 # Convert to serving URL
                 # Assuming we will map data/ to /data_static or similar.
                 # Since I haven't set up the route yet, I'll use a relative path that might fail until step 6.
                 # Let's assume standard static serving of data/
                 img_path = f"/storage_images/{self.state['selected_collection_file'].replace('.json','')}/{os.path.basename(img_path)}"

             with ui.element('div').classes('relative w-full h-48 bg-black'):
                 if img_path:
                     ui.image(img_path).classes('w-full h-full object-cover')
                 else:
                     # Icon fallback
                     ui.icon('inventory_2', size='4em', color='grey').classes('absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2')

                 ui.label(storage.type).classes('absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded')

             with ui.column().classes('p-4 w-full'):
                 ui.label(storage.name).classes('text-lg font-bold text-white truncate w-full')
                 ui.label(f"{count} Cards").classes('text-sm text-gray-400')
                 ui.label(f"${value:,.2f}").classes('text-sm text-green-400')
                 if storage.description:
                     ui.label(storage.description).classes('text-xs text-gray-500 line-clamp-2 mt-1')

    async def open_detail_view(self, storage: StorageContainer):
        self.state['selected_storage'] = storage
        self.state['view'] = 'detail'
        self.state['in_storage_view'] = True # Default to showing contents
        self.render_content.refresh()
        await self.load_data() # Triggers apply_detail_filters and refresh

    async def back_to_gallery(self):
        self.state['view'] = 'gallery'
        self.state['selected_storage'] = None
        self.render_content.refresh()

    async def apply_detail_filters(self):
        if not self.state['selected_storage']: return

        # Need to build filtered list of rows
        # This mirrors collection logic but with specific filtering

        # 1. Get all API cards
        # We already loaded api_card_map

        # 2. Build Rows - but only for owned cards in scope?
        # Or do we show all cards and highlight?
        # Requirement: "The user also has FULL FILTERS AND SEARCH AND SORT OPTIONS. Only the COLLECTORS gallery view."
        # "in storage = False shows ... cards in the COLLECTION that are NOT IN ANY storage."
        # "in storage = True shows only the cards in the selected storage."

        # So in both cases, we iterate ONLY over the Collection cards. We do NOT show unowned cards (unless filters allow? "FULL FILTERS" implies maybe unowned too?)
        # "shows the (filtered) view of all cards in the COLLECTION" -> Implies only owned.

        rows = []
        col = self.state['current_collection']
        if not col: return

        # Target Storage Name for "In Storage" mode
        target_storage = self.state['selected_storage'].name if self.state['in_storage_view'] else None

        # Iterating collection
        for card in col.cards:
            api_card = self.api_card_map.get(card.card_id)
            if not api_card: continue

            for variant in card.variants:
                # Group entries by distinct attributes appropriate for collectors view
                # Collectors View splits by Set Code + Rarity.
                # But here we have specific physical copies potentially.
                # If I have 3 NM entries, do I show 3 cards? Or 1 card with qty 3?
                # "Right click adds/subtracts a card... NEVER CHANGE THE QUANTITY... splitting db entry"
                # This implies we are managing quantities.
                # So we aggregate by (Language, Condition, First Edition).

                # Filter entries based on mode
                relevant_entries = []
                for e in variant.entries:
                    if self.state['in_storage_view']:
                        if e.storage_location == target_storage:
                            relevant_entries.append(e)
                    else:
                        if e.storage_location is None: # "NOT IN ANY storage" -> strictly None? Or not in *current*?
                            # Requirement: "cards in the COLLECTION that are NOT IN ANY storage." -> None.
                            relevant_entries.append(e)

                if not relevant_entries: continue

                # Aggregate
                grouped = {}
                for e in relevant_entries:
                    k = (e.language, e.condition, e.first_edition)
                    grouped[k] = grouped.get(k, 0) + e.quantity

                # Create Rows
                for (lang, cond, first), qty in grouped.items():
                    # Construct Row Object (dict or object)
                    # We can reuse CollectorRow-like dict

                    # Image
                    img_url = api_card.card_images[0].image_url_small if api_card.card_images else None
                    if variant.image_id:
                         # Find image url
                         for img in api_card.card_images:
                             if img.id == variant.image_id:
                                 img_url = img.image_url_small
                                 break

                    # Resolve Set Name
                    set_name = "Unknown"
                    price = 0.0
                    if api_card.card_sets:
                        for s in api_card.card_sets:
                            if s.set_code == variant.set_code:
                                set_name = s.set_name
                                try: price = float(s.set_price)
                                except: pass
                                break

                    row = {
                        'api_card': api_card,
                        'set_code': variant.set_code,
                        'set_name': set_name,
                        'rarity': variant.rarity,
                        'price': price,
                        'image_url': img_url,
                        'image_id': variant.image_id,
                        'variant_id': variant.variant_id,
                        'quantity': qty,
                        'language': lang,
                        'condition': cond,
                        'first_edition': first,
                        'storage_location': target_storage # The location where these cards ARE (or None)
                    }
                    rows.append(row)

        # Apply Filters
        res = rows

        # Search
        txt = self.state['search_text'].lower()
        if txt:
            res = [r for r in res if txt in r['api_card'].name.lower()]

        # Standard Filters (Rarity, Type, etc)
        # Copied logic from CollectionPage...
        if self.state['filter_rarity']:
             r = self.state['filter_rarity'].lower()
             res = [c for c in res if c['rarity'].lower() == r]

        if self.state['filter_card_type']:
             ctypes = self.state['filter_card_type']
             res = [c for c in res if any(t in c['api_card'].type for t in ctypes)]

        if self.state['filter_attr']:
            res = [c for c in res if c['api_card'].attribute == self.state['filter_attr']]

        if self.state['filter_monster_race']:
             res = [c for c in res if "Monster" in c['api_card'].type and c['api_card'].race == self.state['filter_monster_race']]

        if self.state['filter_st_race']:
             res = [c for c in res if ("Spell" in c['api_card'].type or "Trap" in c['api_card'].type) and c['api_card'].race == self.state['filter_st_race']]

        if self.state['filter_archetype']:
             res = [c for c in res if c['api_card'].archetype == self.state['filter_archetype']]

        if self.state['filter_monster_category']:
             categories = self.state['filter_monster_category']
             if isinstance(categories, list) and categories:
                 res = [c for c in res if all(c['api_card'].matches_category(cat) for cat in categories)]

        if self.state['filter_level']:
             res = [c for c in res if c['api_card'].level == int(self.state['filter_level'])]

        atk_min, atk_max = self.state['filter_atk_min'], self.state['filter_atk_max']
        if atk_min > 0 or atk_max < 5000:
             res = [c for c in res if c['api_card'].atk is not None and atk_min <= int(c['api_card'].atk) <= atk_max]

        def_min, def_max = self.state['filter_def_min'], self.state['filter_def_max']
        if def_min > 0 or def_max < 5000:
             res = [c for c in res if getattr(c['api_card'], 'def_', None) is not None and def_min <= getattr(c['api_card'], 'def_', -1) <= def_max]

        if self.state['filter_condition']:
            conds = self.state['filter_condition']
            res = [c for c in res if c['condition'] in conds]

        if self.state['filter_owned_lang']:
            target_lang = self.state['filter_owned_lang']
            res = [c for c in res if c['language'] == target_lang]

        # Ownership & Price
        min_q = self.state['filter_ownership_min']
        max_q = self.state['filter_ownership_max']
        res = [c for c in res if min_q <= c['quantity'] <= max_q]

        p_min = self.state['filter_price_min']
        p_max = self.state['filter_price_max']
        res = [c for c in res if p_min <= c['price'] <= p_max]

        # Sort
        key = self.state['sort_by']
        desc = self.state['sort_descending']

        if key == 'Name':
            res.sort(key=lambda x: x['api_card'].name, reverse=desc)
        elif key == 'Price':
            res.sort(key=lambda x: x['price'], reverse=desc)
        # ...

        self.state['filtered_cards'] = res
        self.state['total_pages'] = (len(res) + self.state['page_size'] - 1) // self.state['page_size']
        if self.state['page'] > self.state['total_pages']: self.state['page'] = 1

        if self.state['view'] == 'detail':
            self.render_detail_grid.refresh()
            self.render_detail_header.refresh()

    async def handle_card_right_click(self, row):
        # Move 1 copy
        # If in_storage_view=True: Remove 1 from Storage (Move to None)
        # If in_storage_view=False: Add 1 to Storage (Move from None to Storage)

        target_storage = self.state['selected_storage'].name

        if self.state['in_storage_view']:
            # Moving FROM Storage TO None
            src = target_storage
            dst = None
            success_msg = f"Removed 1 {row['api_card'].name} from {target_storage}"
        else:
            # Moving FROM None TO Storage
            src = None
            dst = target_storage
            success_msg = f"Added 1 {row['api_card'].name} to {target_storage}"

        success = CollectionEditor.move_card(
            collection=self.state['current_collection'],
            api_card=row['api_card'],
            set_code=row['set_code'],
            rarity=row['rarity'],
            language=row['language'],
            quantity=1,
            condition=row['condition'],
            first_edition=row['first_edition'],
            source_storage=src,
            target_storage=dst,
            image_id=row['image_id'],
            variant_id=row['variant_id']
        )

        if success:
            await run.io_bound(persistence.save_collection, self.state['current_collection'], self.state['selected_collection_file'])
            ui.notify(success_msg, type='positive', position='top')
            await self.apply_detail_filters() # Refresh view
        else:
            ui.notify("Failed to move card (Quantity insufficient?)", type='negative')

    @ui.refreshable
    def render_detail_header(self):
        s = self.state['selected_storage']
        if not s: return

        with ui.row().classes('w-full items-center justify-between mb-4 p-4 bg-gray-900 rounded border border-gray-700'):
            with ui.column():
                ui.label(s.name).classes('text-h4 text-white')
                ui.label(s.type).classes('text-gray-400')

            with ui.row().classes('items-center gap-4'):
                # Edit Button
                ui.button('Edit Storage', icon='edit', on_click=lambda: self.open_storage_dialog(s)).props('flat color=white')

                # Delete Button
                async def delete():
                    # Confirm
                    with ui.dialog() as d, ui.card():
                        ui.label('Delete Storage?').classes('text-h6')
                        ui.label('All cards in this storage will be moved to "Loose" (No Location).').classes('text-sm text-red-400')
                        with ui.row().classes('w-full justify-end'):
                            ui.button('Cancel', on_click=d.close).props('flat')
                            ui.button('Delete', on_click=lambda: d.close(True)).props('color=negative')

                    if await d:
                        storage_service.delete_storage(self.state['current_collection'], s.name)
                        await run.io_bound(persistence.save_collection, self.state['current_collection'], self.state['selected_collection_file'])
                        ui.notify('Storage deleted')
                        await self.back_to_gallery()

                ui.button('Delete', icon='delete', on_click=delete).props('flat color=negative')

                ui.separator().props('vertical')
                ui.button('Back', icon='arrow_back', on_click=self.back_to_gallery).props('flat color=white')

    @ui.refreshable
    def render_detail_grid(self):
        # Pagination Slice
        all_rows = self.state['filtered_cards']
        start = (self.state['page'] - 1) * self.state['page_size']
        end = min(start + self.state['page_size'], len(all_rows))
        rows = all_rows[start:end]

        # Grid
        with ui.grid(columns='repeat(auto-fill, minmax(180px, 1fr))').classes('w-full gap-4'):
            for row in rows:
                self.render_card_item(row)

        # Pagination Controls
        if self.state['total_pages'] > 1:
            with ui.row().classes('w-full justify-center mt-4 gap-2'):
                ui.button(icon='chevron_left', on_click=lambda: self.change_page(-1)).props('flat dense').set_enabled(self.state['page'] > 1)
                ui.label(f"{self.state['page']} / {self.state['total_pages']}").classes('text-white')
                ui.button(icon='chevron_right', on_click=lambda: self.change_page(1)).props('flat dense').set_enabled(self.state['page'] < self.state['total_pages'])

    def change_page(self, delta):
        self.state['page'] += delta
        self.render_detail_grid.refresh()

    def render_card_item(self, row):
        # Right click handler
        async def on_right_click(e):
             e.prevent_default()
             await self.handle_card_right_click(row)

        # Re-use visual style from Collection
        img_src = row['image_url']
        # Local override
        if row['image_id'] and image_manager.image_exists(row['image_id']):
            img_src = f"/images/{row['image_id']}.jpg"

        with ui.card().classes('collection-card w-full p-0 cursor-pointer opacity-100 border border-gray-700 hover:scale-105 transition-transform') \
                .on('contextmenu', on_right_click): # contextmenu is right click

            with ui.element('div').classes('relative w-full aspect-[2/3] bg-black'):
                if img_src: ui.image(img_src).classes('w-full h-full object-cover')

                # Quantity Badge
                ui.label(str(row['quantity'])).classes('absolute top-1 right-1 bg-accent text-dark font-bold px-2 rounded-full text-xs')

                # Info overlay
                with ui.row().classes('absolute bottom-0 left-0 bg-black/80 text-white text-[10px] px-1 gap-1 items-center rounded-tr'):
                    ui.label(row['condition'][:2].upper()).classes('font-bold text-yellow-500')
                    if row['first_edition']: ui.label('1st').classes('font-bold text-orange-400')

                ui.label(row['set_code']).classes('absolute bottom-0 right-0 bg-black/80 text-white text-[10px] px-1 font-mono rounded-tl')

            with ui.column().classes('p-2 gap-0 w-full'):
                ui.label(row['api_card'].name).classes('text-xs font-bold truncate w-full')
                ui.label(row['rarity']).classes('text-[10px] text-gray-400')

            # Tooltip
            with ui.tooltip().classes('bg-transparent p-0'):
                 if img_src: ui.image(img_src).classes('w-64 rounded shadow-lg')

    @ui.refreshable
    def render_content(self):
        if self.state['view'] == 'gallery':
            self.render_gallery()
        else:
            self.render_detail_header()

            # Detail Controls (Toggle, Filters)
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                # In Storage Toggle
                ui.label("Show:").classes('text-gray-400')

                def toggle(val):
                    self.state['in_storage_view'] = val
                    self.state['page'] = 1
                    # Refresh
                    asyncio.create_task(self.apply_detail_filters())

                with ui.button_group():
                    ui.button('Loose Cards', on_click=lambda: toggle(False)).props(f'flat={self.state["in_storage_view"]} color=accent')
                    ui.button(f'In {self.state["selected_storage"].name}', on_click=lambda: toggle(True)).props(f'flat={not self.state["in_storage_view"]} color=accent')

                ui.space()

                # Filter Trigger
                ui.button('Filters', icon='filter_list', on_click=self.filter_dialog.open).props('color=primary')

            self.render_detail_grid()

    def build_ui(self):
        # Filter Dialog
        self.filter_dialog = ui.dialog().props('position=right')
        with self.filter_dialog, ui.card().classes('h-full w-96 bg-gray-900 border-l border-gray-700 p-0 flex flex-col'):
             with ui.scroll_area().classes('flex-grow w-full'):
                 self.filter_pane = FilterPane(self.state, self.apply_detail_filters, self.load_data) # Reset callback reloads data?
                 self.filter_pane.build()

        self.render_content()

        # Initial Load
        ui.timer(0.1, self.load_data, once=True)

def storage_page():
    page = StoragePage()
    page.build_ui()
