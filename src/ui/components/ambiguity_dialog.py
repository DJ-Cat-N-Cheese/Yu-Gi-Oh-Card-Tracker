from nicegui import ui
from typing import Dict, Any, List, Optional, Callable
import logging

from src.core.utils import is_set_code_compatible, REGION_TO_LANGUAGE_MAP
from src.services.ygo_api import ygo_service
from src.services.image_manager import image_manager

logger = logging.getLogger(__name__)

class AmbiguityDialog(ui.dialog):
    def __init__(self, scan_result: Dict[str, Any], on_confirm: Callable):
        super().__init__()
        self.result = scan_result
        self.candidates = scan_result.get('candidates', [])
        self.on_confirm_cb = on_confirm

        # Initial Selection (Best Guess)
        self.selected_set_code = scan_result.get('set_code')
        self.selected_rarity = scan_result.get('rarity') or scan_result.get('visual_rarity')
        self.selected_language = scan_result.get('language', 'EN')
        self.selected_first_ed = scan_result.get('first_edition', False)

        # Try to find best candidate to init image
        best_cand = self.candidates[0] if self.candidates else {}
        self.selected_image_id = best_cand.get('image_id')
        self.card_id = best_cand.get('card_id')
        self.card_name = best_cand.get('name', 'Unknown')

        # UI State
        self.preview_image = None
        self.rarity_select = None
        self.set_code_select = None

        with self, ui.card().classes('w-[800px] h-[600px] flex flex-row p-4 gap-4'):
             # LEFT: Image Preview
             with ui.column().classes('w-1/3 h-full items-center justify-center bg-black rounded'):
                 self.preview_image = ui.image().classes('max-w-full max-h-full object-contain')
                 self.update_preview()

             # RIGHT: Controls
             with ui.column().classes('flex-grow h-full'):
                 ui.label("Resolve Ambiguity").classes('text-xl font-bold mb-2')
                 ui.label(self.card_name).classes('text-lg font-bold text-primary mb-4')

                 # 1. Language
                 ui.select(
                     options=['EN', 'DE', 'FR', 'IT', 'ES', 'PT', 'JP', 'KR'],
                     value=self.selected_language,
                     label="Language",
                     on_change=self.on_language_change
                 ).classes('w-full')

                 # 2. Set Code
                 self.set_code_select = ui.select(
                     options=self.get_set_code_options(),
                     value=self.selected_set_code,
                     label="Set Code",
                     on_change=self.on_set_code_change,
                     with_input=True
                 ).classes('w-full')

                 # 3. Rarity
                 self.rarity_select = ui.select(
                     options=self.get_rarity_options(),
                     value=self.selected_rarity,
                     label="Rarity",
                     on_change=self.on_rarity_change
                 ).classes('w-full')

                 # 4. 1st Edition
                 ui.checkbox("1st Edition", value=self.selected_first_ed,
                             on_change=lambda e: setattr(self, 'selected_first_ed', e.value)).classes('mt-2')

                 ui.space()

                 # Buttons
                 with ui.row().classes('w-full justify-end gap-2'):
                     ui.button("Cancel", on_click=self.close, color='secondary')
                     ui.button("Confirm", on_click=self.confirm, color='primary')

    def get_set_code_options(self):
        codes = set()
        for c in self.candidates:
            # Check country code logic using utility
            if is_set_code_compatible(c['set_code'], self.selected_language):
                codes.add(c['set_code'])

        # Ensure current selection is in list if compatible
        if self.selected_set_code and is_set_code_compatible(self.selected_set_code, self.selected_language):
            codes.add(self.selected_set_code)

        return sorted(list(codes))

    def get_rarity_options(self):
        # Based on selected set code, what rarities are available?
        rarities = set()
        for c in self.candidates:
            if c['set_code'] == self.selected_set_code:
                rarities.add(c['rarity'])
        return sorted(list(rarities))

    def on_language_change(self, e):
        self.selected_language = e.value
        # Update set codes
        opts = self.get_set_code_options()
        self.set_code_select.options = opts
        if opts and self.selected_set_code not in opts:
            self.selected_set_code = opts[0]
        self.set_code_select.value = self.selected_set_code
        self.set_code_select.update()

        # Trigger set code change to update rarities
        self.on_set_code_change({'value': self.selected_set_code})

    def on_set_code_change(self, e):
        # Handle dict or direct value from select
        val = e['value'] if isinstance(e, dict) else e.value
        self.selected_set_code = val

        # Update rarities
        opts = self.get_rarity_options()
        self.rarity_select.options = opts
        if opts and self.selected_rarity not in opts:
            self.selected_rarity = opts[0]
        self.rarity_select.value = self.selected_rarity
        self.rarity_select.update()

        # Update Image ID based on set code + rarity (best effort)
        self.update_image_selection()

    def on_rarity_change(self, e):
        self.selected_rarity = e.value
        self.update_image_selection()

    def update_image_selection(self):
        # Find candidate matching code + rarity
        cand = next((c for c in self.candidates if c['set_code'] == self.selected_set_code and c['rarity'] == self.selected_rarity), None)
        if cand:
            self.selected_image_id = cand['image_id']
            self.update_preview()

    def update_preview(self):
        if self.selected_image_id:
             self.preview_image.set_source(f"/images/{self.selected_image_id}.jpg")
        else:
             self.preview_image.set_source(None)

    def confirm(self):
        # Construct updated result
        final_res = self.result.copy()
        final_res['set_code'] = self.selected_set_code
        final_res['rarity'] = self.selected_rarity
        final_res['language'] = self.selected_language
        final_res['first_edition'] = self.selected_first_ed
        final_res['name'] = self.card_name
        final_res['card_id'] = self.card_id

        # If user selected a specific combo, we might have exact variant ID
        cand = next((c for c in self.candidates if c['set_code'] == self.selected_set_code and c['rarity'] == self.selected_rarity), None)
        if cand:
            final_res['variant_id'] = cand.get('variant_id')
            final_res['image_id'] = cand.get('image_id')

        self.on_confirm_cb(final_res)
        self.close()
