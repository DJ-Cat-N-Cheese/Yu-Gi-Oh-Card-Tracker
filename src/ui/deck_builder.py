from nicegui import ui, run
from src.core.persistence import persistence
from src.core.models import Deck, Collection
from src.services.ygo_api import ygo_service, ApiCard
from src.services.image_manager import image_manager
from src.core.config import config_manager
from src.ui.components.filter_pane import FilterPane
from src.ui.components.single_card_view import SingleCardView
from dataclasses import dataclass
from typing import List, Optional, Dict, Set
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class DeckCardViewModel:
    api_card: ApiCard
    quantity: int
    is_owned: bool # Owned in the reference collection
    owned_quantity: int
    side_quantity: int = 0
    extra_quantity: int = 0
    main_quantity: int = 0

class DeckBuilderPage:
    def __init__(self):
        self.state = {
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

            'sort_by': 'Name',
            'sort_descending': False,

            'current_deck': None, # Deck object
            'current_deck_name': None,
            'reference_collection': None, # Collection object for ownership check

            'available_decks': [],
            'available_collections': [],

            'all_api_cards': [], # List[ApiCard]
            'filtered_items': [], # List[ApiCard] for search results

            'page': 1,
            'page_size': 48,
            'total_pages': 1,

            'view_mode': 'grid', # For deck view
            'loading': False
        }

        self.single_card_view = SingleCardView()
        self.filter_pane: Optional[FilterPane] = None
        self.api_card_map = {} # ID -> ApiCard

    async def load_initial_data(self):
        self.state['loading'] = True
        try:
            # Load API Data
            lang = config_manager.get_language()
            api_cards = await ygo_service.load_card_database(lang)
            self.state['all_api_cards'] = api_cards
            self.api_card_map = {c.id: c for c in api_cards}

            # Setup Filters Metadata
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
            self.state['available_card_types'] = ['Monster', 'Spell', 'Trap', 'Skill']

            # Load Decks List
            self.state['available_decks'] = persistence.list_decks()

            # Load Collections List (for reference)
            cols = persistence.list_collections()
            self.state['available_collections'] = cols
            if cols:
                # Load first collection as default reference
                try:
                    self.state['reference_collection'] = await run.io_bound(persistence.load_collection, cols[0])
                except Exception as e:
                    logger.error(f"Failed to load default reference collection: {e}")

            # Apply initial filters
            await self.apply_filters()
            self.filter_pane.update_options()

        except Exception as e:
            logger.error(f"Error loading initial data: {e}", exc_info=True)
            ui.notify(f"Error loading data: {e}", type='negative')
        finally:
            self.state['loading'] = False
            self.render_header.refresh()
            self.search_results_area.refresh()

    async def load_deck(self, filename):
        try:
            deck = await run.io_bound(persistence.load_deck, filename)
            self.state['current_deck'] = deck
            self.state['current_deck_name'] = filename.replace('.ydk', '')
            self.render_deck_area.refresh()
            self.render_header.refresh()
            ui.notify(f"Loaded deck: {self.state['current_deck_name']}", type='positive')
        except Exception as e:
            logger.error(f"Error loading deck {filename}: {e}")
            ui.notify(f"Error loading deck: {e}", type='negative')

    async def save_current_deck(self):
        if not self.state['current_deck'] or not self.state['current_deck_name']:
            return
        try:
            filename = f"{self.state['current_deck_name']}.ydk"
            await run.io_bound(persistence.save_deck, self.state['current_deck'], filename)
            ui.notify('Deck saved.', type='positive')
            # Refresh list in case it was new
            self.state['available_decks'] = persistence.list_decks()
            self.render_header.refresh()
        except Exception as e:
            logger.error(f"Error saving deck: {e}")
            ui.notify(f"Error saving deck: {e}", type='negative')

    async def create_new_deck(self, name):
        if not name: return
        filename = f"{name}.ydk"
        if filename in self.state['available_decks']:
             ui.notify("Deck already exists!", type='warning')
             return

        new_deck = Deck(name=name)
        self.state['current_deck'] = new_deck
        self.state['current_deck_name'] = name
        await self.save_current_deck()
        self.render_header.refresh()
        self.render_deck_area.refresh()

    async def add_card_to_deck(self, card_id: int, quantity: int, target: str):
        if not self.state['current_deck']:
            ui.notify("Please select or create a deck first.", type='warning')
            return

        deck = self.state['current_deck']
        target_list = getattr(deck, target)

        # Add copies
        for _ in range(quantity):
            target_list.append(card_id)

        await self.save_current_deck()
        self.render_deck_area.refresh()

    async def remove_card_from_deck(self, card_id: int, target: str):
        if not self.state['current_deck']: return

        deck = self.state['current_deck']
        target_list = getattr(deck, target)

        if card_id in target_list:
            target_list.remove(card_id)
            await self.save_current_deck()
            self.render_deck_area.refresh()

    async def apply_filters(self):
        source = self.state['all_api_cards']
        res = list(source)

        txt = self.state['search_text'].lower()
        if txt:
             res = [c for c in res if txt in c.name.lower() or txt in c.type.lower() or txt in c.desc.lower()]

        # Reuse similar filtering logic from CollectionPage (simplified for brevity here, can expand)
        # Type
        if self.state['filter_card_type']:
             ctypes = self.state['filter_card_type']
             if isinstance(ctypes, str): ctypes = [ctypes]
             res = [c for c in res if any(t in c.type for t in ctypes)]

        # Attribute
        if self.state['filter_attr']:
             res = [c for c in res if c.attribute == self.state['filter_attr']]

        # Race/Archetype...
        if self.state['filter_monster_race']:
             res = [c for c in res if "Monster" in c.type and c.race == self.state['filter_monster_race']]
        if self.state['filter_st_race']:
             res = [c for c in res if ("Spell" in c.type or "Trap" in c.type) and c.race == self.state['filter_st_race']]
        if self.state['filter_archetype']:
             res = [c for c in res if c.archetype == self.state['filter_archetype']]

        # Level/ATK/DEF
        if self.state['filter_level']:
             res = [c for c in res if c.level == int(self.state['filter_level'])]

        atk_min, atk_max = self.state['filter_atk_min'], self.state['filter_atk_max']
        if atk_min > 0 or atk_max < 5000:
             res = [c for c in res if c.atk is not None and atk_min <= int(c.atk) <= atk_max]

        # Sorting
        key = self.state['sort_by']
        reverse = self.state['sort_descending']

        if key == 'Name':
            res.sort(key=lambda x: x.name, reverse=reverse)
        elif key == 'ATK':
            res.sort(key=lambda x: (x.atk or -1), reverse=reverse)
        elif key == 'DEF':
            res.sort(key=lambda x: (getattr(x, 'def_', None) or -1), reverse=reverse)
        elif key == 'Level':
            res.sort(key=lambda x: (x.level or -1), reverse=reverse)
        elif key == 'Newest':
            res.sort(key=lambda x: x.id, reverse=reverse)

        self.state['filtered_items'] = res
        self.state['page'] = 1
        self.update_pagination()

        # Prepare images for current page
        await self.prepare_current_page_images()
        self.search_results_area.refresh()

    def update_pagination(self):
        count = len(self.state['filtered_items'])
        self.state['total_pages'] = (count + self.state['page_size'] - 1) // self.state['page_size']

    async def prepare_current_page_images(self):
        start = (self.state['page'] - 1) * self.state['page_size']
        end = min(start + self.state['page_size'], len(self.state['filtered_items']))
        items = self.state['filtered_items'][start:end]
        if not items: return

        url_map = {}
        for card in items:
             if card.card_images:
                 url_map[card.card_images[0].id] = card.card_images[0].image_url_small

        if url_map:
             await image_manager.download_batch(url_map, concurrency=5)

    async def reset_filters(self):
        self.state.update({
            'search_text': '',
            'filter_set': '',
            'filter_rarity': '',
            'filter_attr': '',
            'filter_card_type': ['Monster', 'Spell', 'Trap'],
            # ... reset others ...
            'filter_level': None,
            'filter_atk_min': 0, 'filter_atk_max': 5000,
            # ...
        })
        if self.filter_pane: self.filter_pane.reset_ui_elements()
        await self.apply_filters()

    # --- UI Renderers ---

    @ui.refreshable
    def render_header(self):
        with ui.row().classes('w-full items-center gap-4 q-mb-md p-4 bg-gray-900 rounded-lg border border-gray-800'):
            ui.label('Deck Builder').classes('text-h5')

            # Deck Selector
            deck_options = {f: f.replace('.ydk', '') for f in self.state['available_decks']}
            deck_options['__NEW__'] = '+ New Deck'

            async def on_deck_change(e):
                if e.value == '__NEW__':
                    # Open Dialog
                    with ui.dialog() as d, ui.card().classes('w-96'):
                         ui.label('Create New Deck').classes('text-h6')

                         with ui.tabs().classes('w-full') as tabs:
                             t_new = ui.tab('New Empty')
                             t_import = ui.tab('Import .ydk')

                         with ui.tab_panels(tabs, value=t_new).classes('w-full'):
                             with ui.tab_panel(t_new):
                                 name_input = ui.input('Deck Name').classes('w-full')
                                 async def create():
                                     await self.create_new_deck(name_input.value)
                                     d.close()
                                 ui.button('Create', on_click=create).props('color=positive').classes('w-full q-mt-md')

                             with ui.tab_panel(t_import):
                                 ui.label('Select .ydk file').classes('text-sm text-grey')

                                 async def handle_upload(e):
                                     try:
                                         content = e.content.read().decode('utf-8')
                                         name = e.name.replace('.ydk', '')
                                         # Create temp file and load it, or better: Parse content directly
                                         # Since load_deck takes a filename, I should save it first or refactor load_deck.
                                         # I'll save it directly.
                                         filename = f"{name}.ydk"
                                         filepath = f"data/decks/{filename}"
                                         with open(filepath, 'w', encoding='utf-8') as f:
                                             f.write(content)

                                         await self.load_deck(filename)
                                         d.close()
                                         ui.notify(f"Imported deck: {name}", type='positive')
                                     except Exception as ex:
                                         ui.notify(f"Error importing: {ex}", type='negative')

                                 ui.upload(on_upload=handle_upload, auto_upload=True).props('accept=.ydk').classes('w-full')

                    d.open()
                    # Reset selector logic handled by refresh
                elif e.value:
                    await self.load_deck(e.value)

            selected = f"{self.state['current_deck_name']}.ydk" if self.state['current_deck_name'] else None
            ui.select(deck_options, value=selected, label='Current Deck', on_change=on_deck_change).classes('min-w-[200px]')

            # Reference Collection Selector
            col_options = {f: f.replace('.json', '') for f in self.state['available_collections']}
            async def on_col_change(e):
                if e.value:
                     self.state['reference_collection'] = await run.io_bound(persistence.load_collection, e.value)
                     self.render_deck_area.refresh()

            curr_col_file = None # We don't track filename in state easily right now, but we can default
            ui.select(col_options, label='Reference Collection', on_change=on_col_change).classes('min-w-[200px]')

            ui.space()

            # Search Input
            async def on_search(e):
                self.state['search_text'] = e.value
                await self.apply_filters()
            ui.input(placeholder='Search cards...', on_change=on_search).props('debounce=300 icon=search').classes('w-64')

            with ui.button_group():
                is_grid = self.state['view_mode'] == 'grid'
                with ui.button(icon='grid_view', on_click=lambda: [self.state.update({'view_mode': 'grid'}), self.render_deck_area.refresh(), self.render_header.refresh()]) \
                    .props(f'flat={not is_grid} color=accent'):
                    ui.tooltip('Grid View')
                with ui.button(icon='list', on_click=lambda: [self.state.update({'view_mode': 'list'}), self.render_deck_area.refresh(), self.render_header.refresh()]) \
                    .props(f'flat={is_grid} color=accent'):
                    ui.tooltip('List View')

            with ui.button(icon='filter_list', on_click=self.filter_dialog.open).props('color=primary'):
                ui.tooltip('Filters')

    @ui.refreshable
    def search_results_area(self):
        start = (self.state['page'] - 1) * self.state['page_size']
        end = min(start + self.state['page_size'], len(self.state['filtered_items']))
        items = self.state['filtered_items'][start:end]

        # Pagination Controls
        with ui.row().classes('w-full items-center justify-between q-mb-xs px-2'):
            ui.label(f"{start+1}-{end} of {len(self.state['filtered_items'])}").classes('text-xs text-grey')
            with ui.row().classes('gap-1'):
                 async def change_page(delta):
                     new_p = max(1, min(self.state['total_pages'], self.state['page'] + delta))
                     if new_p != self.state['page']:
                         self.state['page'] = new_p
                         await self.prepare_current_page_images()
                         self.search_results_area.refresh()

                 ui.button(icon='chevron_left', on_click=lambda: change_page(-1)).props('flat dense size=sm')
                 ui.button(icon='chevron_right', on_click=lambda: change_page(1)).props('flat dense size=sm')

        with ui.column().classes('w-full h-full border border-gray-800 rounded p-2 overflow-y-auto block'):
            if not items:
                ui.label('No cards found.').classes('text-grey italic w-full text-center')
                return

            # Render Grid
            with ui.grid(columns='repeat(auto-fill, minmax(100px, 1fr))').classes('w-full gap-2'):
                for card in items:
                     img_id = card.card_images[0].id if card.card_images else card.id
                     img_src = f"/images/{img_id}.jpg" if image_manager.image_exists(img_id) else (card.card_images[0].image_url_small if card.card_images else None)

                     with ui.card().classes('p-0 cursor-pointer hover:scale-105 transition-transform border border-gray-800') \
                        .on('click', lambda c=card: self.single_card_view.open_deck_builder(c, self.add_card_to_deck)):
                         ui.image(img_src).classes('w-full aspect-[2/3] object-cover')
                         with ui.column().classes('p-1 gap-0'):
                             ui.label(card.name).classes('text-[10px] font-bold truncate w-full leading-tight')
                             ui.label(f"{card.atk or '-'}/{getattr(card, 'def_', '-') or '-'}").classes('text-[9px] text-gray-400')


    @ui.refreshable
    def render_deck_area(self):
        deck = self.state['current_deck']
        if not deck:
            ui.label('Select or create a deck to start building.').classes('text-xl text-grey w-full text-center q-mt-xl')
            return

        # Prepare deck cards
        def get_cards(ids):
            cards = []
            for cid in ids:
                if cid in self.api_card_map:
                    cards.append(self.api_card_map[cid])
                else:
                    # Handle unknown cards?
                    pass
            return cards

        main_cards = get_cards(deck.main)
        extra_cards = get_cards(deck.extra)
        side_cards = get_cards(deck.side)

        # Check Ownership
        ref_col = self.state['reference_collection']
        owned_map = {} # card_id -> quantity
        if ref_col:
            for c in ref_col.cards:
                owned_map[c.card_id] = c.total_quantity

        def render_section(title, cards, target, max_count):
            count = len(cards)
            color = 'text-white'
            if count < 40 and target == 'main': color = 'text-red-400'
            elif count > 60 and target == 'main': color = 'text-red-400'

            with ui.column().classes('w-full h-full bg-dark border border-gray-700 p-2 rounded flex flex-col'):
                ui.label(f"{title} ({count})").classes(f'font-bold {color} q-mb-sm text-xs uppercase tracking-wider')

                with ui.column().classes('flex-grow w-full bg-black/20 rounded p-2 overflow-y-auto block'):
                     def sort_key(c):
                         # Monster, Spell, Trap
                         t = 0
                         if "Monster" in c.type: t=0
                         elif "Spell" in c.type: t=1
                         elif "Trap" in c.type: t=2
                         return (t, c.name)

                     cards.sort(key=sort_key)
                     deck_counts = {}
                     for c in cards: deck_counts[c.id] = deck_counts.get(c.id, 0) + 1

                     if self.state['view_mode'] == 'grid':
                         with ui.grid(columns='repeat(auto-fill, minmax(60px, 1fr))').classes('w-full gap-2'):
                             for i, card in enumerate(cards):
                                  img_id = card.card_images[0].id if card.card_images else card.id
                                  img_src = f"/images/{img_id}.jpg" if image_manager.image_exists(img_id) else (card.card_images[0].image_url_small if card.card_images else None)

                                  needed = deck_counts[card.id]
                                  owned = owned_map.get(card.id, 0)
                                  is_missing = owned < needed

                                  border_class = 'border-red-500 border-2' if is_missing else 'border-transparent'
                                  opacity = 'opacity-100'
                                  if is_missing and owned == 0: opacity = 'opacity-50 grayscale'

                                  with ui.card().classes(f'p-0 cursor-pointer relative group {border_class} {opacity}') \
                                    .on('click', lambda c=card, t=target: self.remove_card_from_deck(c.id, t)):
                                      ui.image(img_src).classes('w-full aspect-[2/3] object-cover rounded')
                                      # Hover remove icon
                                      with ui.element('div').classes('absolute inset-0 bg-black/50 hidden group-hover:flex items-center justify-center'):
                                          ui.icon('remove', color='white').classes('text-2xl')
                     else:
                        # List View
                        with ui.column().classes('w-full gap-1'):
                             unique_cards = []
                             seen = set()
                             for c in cards:
                                 if c.id not in seen:
                                     unique_cards.append(c)
                                     seen.add(c.id)

                             for card in unique_cards:
                                 qty = deck_counts[card.id]
                                 owned = owned_map.get(card.id, 0)
                                 missing = max(0, qty - owned)

                                 bg_color = 'bg-gray-800'
                                 text_color = 'text-white'
                                 if missing > 0:
                                     bg_color = 'bg-red-900/30'
                                     text_color = 'text-red-300'

                                 with ui.row().classes(f'w-full {bg_color} p-1 items-center rounded cursor-pointer group hover:bg-white/10') \
                                    .on('click', lambda c=card, t=target: self.remove_card_from_deck(c.id, t)):

                                     ui.label(str(qty)).classes('font-bold w-6 text-center')
                                     ui.label(card.name).classes(f'flex-grow truncate text-xs {text_color} font-bold')
                                     ui.label(card.type).classes('text-[10px] text-gray-400 w-16 truncate')

                                     if missing > 0:
                                          ui.label(f"Miss: {missing}").classes('text-[10px] text-red-400 font-bold')

                                     ui.icon('remove_circle', color='red').classes('text-xs opacity-0 group-hover:opacity-100 transition-opacity')

        with ui.column().classes('w-full h-full gap-2'):
             # Top: Main Deck (Grow)
             with ui.row().classes('w-full h-3/5'):
                 render_section('Main Deck', main_cards, 'main', 60)

             # Bottom: Extra / Side
             with ui.row().classes('w-full h-2/5 gap-2'):
                 with ui.column().classes('w-1/2 h-full'):
                     render_section('Extra Deck', extra_cards, 'extra', 15)
                 with ui.column().classes('w-1/2 h-full'):
                     render_section('Side Deck', side_cards, 'side', 15)

    def build_ui(self):
        # Filter Dialog
        self.filter_dialog = ui.dialog().props('position=right')
        with self.filter_dialog, ui.card().classes('h-full w-96 bg-gray-900 border-l border-gray-700 p-0 flex flex-col'):
             with ui.scroll_area().classes('flex-grow w-full'):
                 self.filter_pane = FilterPane(self.state, self.apply_filters, self.reset_filters)
                 self.filter_pane.build()

        self.render_header()

        with ui.row().classes('w-full h-[calc(100vh-140px)] gap-2 no-wrap'):
            # Left: Search Results
            with ui.column().classes('w-[350px] shrink-0 h-full bg-dark border border-gray-800 rounded flex flex-col deck-builder-search-results z-50 relative'):
                self.search_results_area()

            # Right: Deck Area
            with ui.column().classes('col h-full relative deck-builder-deck-area overflow-hidden'):
                 self.render_deck_area()

        ui.timer(0.1, self.load_initial_data, once=True)

def deck_builder_page():
    page = DeckBuilderPage()
    page.build_ui()
