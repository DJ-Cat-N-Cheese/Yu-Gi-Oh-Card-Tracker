from nicegui import ui, app, run, events
import logging
import os
import shutil
import asyncio
import time
import uuid
import base64
import queue
import json
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from PIL import Image
import io

# Import the module, not the instance, to avoid stale references on reload
from src.services.scanner import manager as scanner_service
from src.services.scanner import SCANNER_AVAILABLE
from src.core.persistence import persistence
from src.core.models import CollectionCard, CollectionVariant, CollectionEntry, Collection, ApiCard
from src.services.collection_editor import CollectionEditor
from src.services.ygo_api import ygo_service
from src.ui.components.ambiguity_dialog import AmbiguityDialog
from src.ui.components.filter_pane import FilterPane
from src.ui.components.single_card_view import SingleCardView
from src.core.changelog_manager import changelog_manager
from src.services.image_manager import image_manager
from src.core.utils import generate_variant_id, normalize_set_code, extract_language_code, LANGUAGE_COUNTRY_MAP
from src.core.constants import CARD_CONDITIONS, CONDITION_ABBREVIATIONS
from src.core import config_manager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class BulkCollectionEntry:
    id: str # Unique ID for UI
    api_card: ApiCard
    quantity: int
    set_code: str
    set_name: str
    rarity: str
    language: str
    condition: str
    first_edition: bool
    image_url: str
    image_id: int
    variant_id: str
    storage_location: Optional[str] = None
    price: float = 0.0

def _build_collection_entries(col: Collection) -> List[BulkCollectionEntry]:
    entries = []
    # We need api cards to populate details.
    # Since we don't have the full map passed in, we fetch from cache or individual lookups?
    # Individual lookups are slow. We should probably get the map once or pass it.
    # ScanPage handles loading.

    # We'll use ygo_service to get the card map if possible, or lookup per card.
    # Given ScanPage is usually smaller than a full collection, per-card might be okay,
    # but let's try to be efficient.

    # Optimization: Get all card IDs from collection
    card_ids = [c.card_id for c in col.cards]
    # We can pre-fetch these? ygo_service doesn't have a "get_many" but get_card uses cache.
    # We assume ygo_service.load_card_database() has been called or will be called.
    # ScanPage init calls load_recent_scans which happens on init.
    # We might need to ensure DB is loaded.

    for card in col.cards:
        api_card = ygo_service.get_card(card.card_id)
        if not api_card: continue

        for variant in card.variants:
            img_id = variant.image_id if variant.image_id else (api_card.card_images[0].id if api_card.card_images else api_card.id)
            img_url = api_card.card_images[0].image_url_small if api_card.card_images else None
            if variant.image_id and api_card.card_images:
                for img in api_card.card_images:
                    if img.id == variant.image_id:
                        img_url = img.image_url_small
                        break

            set_name = "Unknown Set"
            if api_card.card_sets:
                for s in api_card.card_sets:
                     if s.set_code == variant.set_code:
                         set_name = s.set_name
                         break

            for entry in variant.entries:
                loc_str = str(entry.storage_location) if entry.storage_location else "None"
                unique_id = f"{variant.variant_id}_{entry.language}_{entry.condition}_{entry.first_edition}_{loc_str}"
                entries.append(BulkCollectionEntry(
                    id=unique_id,
                    api_card=api_card,
                    quantity=entry.quantity,
                    set_code=variant.set_code,
                    set_name=set_name,
                    rarity=variant.rarity,
                    language=entry.language,
                    condition=entry.condition,
                    first_edition=entry.first_edition,
                    image_url=img_url,
                    image_id=img_id,
                    variant_id=variant.variant_id,
                    storage_location=entry.storage_location,
                    price=0.0
                ))
    return entries

JS_CAMERA_CODE = """
<script>
window.scannerVideo = null;
window.debugVideo = null;
window.scannerStream = null;
window.overlayCanvas = null;
window.overlayCtx = null;
window.scanner_js_loaded = true;

function initScanner() {
    window.scannerVideo = document.getElementById('scanner-video');
    window.overlayCanvas = document.getElementById('overlay-canvas');
    if (window.overlayCanvas) {
        window.overlayCtx = window.overlayCanvas.getContext('2d');
    }
}

async function startCamera(deviceId) {
    if (!window.scannerVideo) initScanner();
    if (!window.scannerVideo) return false;

    if (window.scannerStream) stopCamera();

    try {
        const constraints = {
            video: {
                deviceId: deviceId ? { exact: deviceId } : undefined,
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        };
        window.scannerStream = await navigator.mediaDevices.getUserMedia(constraints);
        window.scannerVideo.srcObject = window.scannerStream;
        await window.scannerVideo.play();

        attachDebugStream();

        if (window.overlayCanvas) {
            window.overlayCanvas.width = window.scannerVideo.videoWidth;
            window.overlayCanvas.height = window.scannerVideo.videoHeight;
        }

        return true;
    } catch (err) {
        console.error("Error accessing camera:", err);
        return false;
    }
}

function attachDebugStream() {
    window.debugVideo = document.getElementById('debug-video');
    if (window.debugVideo && window.scannerStream) {
        window.debugVideo.srcObject = window.scannerStream;
        window.debugVideo.play().catch(e => console.log("Debug video play error:", e));
    }
}

function initDebugStream() {
    let attempts = 0;
    const interval = setInterval(() => {
        window.debugVideo = document.getElementById('debug-video');
        if (window.debugVideo) {
            clearInterval(interval);
            attachDebugStream();
        } else if (attempts > 10) {
            clearInterval(interval);
        }
        attempts++;
    }, 100);
}

function stopCamera() {
    window.isStreaming = false;
    if (window.streamInterval) {
        clearInterval(window.streamInterval);
        window.streamInterval = null;
    }
    if (window.scannerVideo && window.scannerVideo.srcObject) {
        const tracks = window.scannerVideo.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        window.scannerVideo.srcObject = null;
    }
    if (window.debugVideo) {
        window.debugVideo.srcObject = null;
    }
    clearOverlay();
}

function drawOverlay(points) {
    if (!window.overlayCanvas || !window.overlayCtx || !window.scannerVideo) return;
    const w = window.overlayCanvas.width;
    const h = window.overlayCanvas.height;
    window.overlayCtx.clearRect(0, 0, w, h);

    if (!points || points.length < 4) return;
    window.overlayCtx.beginPath();
    window.overlayCtx.moveTo(points[0][0] * w, points[0][1] * h);
    for (let i = 1; i < points.length; i++) {
        window.overlayCtx.lineTo(points[i][0] * w, points[i][1] * h);
    }
    window.overlayCtx.closePath();
    window.overlayCtx.strokeStyle = '#00FF00';
    window.overlayCtx.lineWidth = 4;
    window.overlayCtx.stroke();
}

function clearOverlay() {
    if (window.overlayCtx && window.overlayCanvas) {
        window.overlayCtx.clearRect(0, 0, window.overlayCanvas.width, window.overlayCanvas.height);
    }
}

async function getVideoDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return [];
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices
            .filter(device => device.kind === 'videoinput')
            .map(device => ({ label: device.label || 'Camera ' + (devices.indexOf(device) + 1), value: device.deviceId }));
    } catch (e) {
        return [];
    }
}

async function captureSingleFrame() {
    let videoSource = window.scannerVideo;
    let usingDebug = false;

    if (!videoSource || videoSource.readyState < 2) {
        if (window.debugVideo && window.debugVideo.readyState >= 2) {
             videoSource = window.debugVideo;
             usingDebug = true;
        } else {
             return null;
        }
    } else {
        if (videoSource.paused || videoSource.ended) {
             if (window.debugVideo && window.debugVideo.readyState >= 2) {
                 videoSource = window.debugVideo;
                 usingDebug = true;
             }
        }
    }

    if (videoSource.paused) {
        try {
            await videoSource.play();
        } catch (e) {
            console.error("Failed to resume video for capture:", e);
        }
    }

    const canvas = document.createElement('canvas');
    canvas.width = videoSource.videoWidth;
    canvas.height = videoSource.videoHeight;
    canvas.getContext('2d').drawImage(videoSource, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.95);
}

function reattachScannerVideo() {
    window.scannerVideo = document.getElementById('scanner-video');
    window.overlayCanvas = document.getElementById('overlay-canvas');
    if (window.overlayCanvas) {
        window.overlayCtx = window.overlayCanvas.getContext('2d');
        if (window.scannerVideo) {
             window.overlayCanvas.width = window.scannerVideo.videoWidth;
             window.overlayCanvas.height = window.scannerVideo.videoHeight;
        }
    }

    if (window.scannerVideo && window.scannerStream) {
        window.scannerVideo.srcObject = window.scannerStream;
        window.scannerVideo.play().catch(console.error);
    }
}

function setRotation(deg) {
    const v1 = document.getElementById('scanner-video');
    const v2 = document.getElementById('debug-video');
    const transform = 'rotate(' + deg + 'deg)';
    if (v1) v1.style.transform = transform;
    if (v2) v2.style.transform = transform;
}
</script>
"""

class ScanPage:
    def __init__(self):
        self.scan_collection = Collection(name="scan_temp", cards=[])
        self.target_collection_file = None
        self.collections = persistence.list_collections()
        if self.collections:
            self.target_collection_file = self.collections[0]

        self.camera_select = None
        self.start_btn = None
        self.stop_btn = None
        self.is_active = False
        self.default_condition = "Near Mint"
        self.default_language = "EN"
        self.default_storage = None
        self.target_collection_obj = None

        # Load Configuration
        self.config = config_manager.load_config()

        # Initialize UI state from config
        self.ocr_tracks = self.config.get('ocr_tracks', ['doctr'])
        # Ensure ocr_tracks is valid (only one active track supported for now, but keeping list structure for compat)
        if not self.ocr_tracks:
            self.ocr_tracks = ['doctr']
        self.selected_track = self.ocr_tracks[0] # For UI Radio Button

        self.preprocessing_mode = self.config.get('preprocessing_mode', 'classic')
        self.art_match_yolo = self.config.get('art_match_yolo', True) # Default to True per request
        self.ambiguity_threshold = self.config.get('ambiguity_threshold', 10.0)
        self.save_warped_scan = self.config.get('save_warped_scan', True)
        self.save_raw_scan = self.config.get('save_raw_scan', True)
        self.art_match_threshold = self.config.get('art_match_threshold', 0.42)
        self.rotation = self.config.get('rotation', 0)

        # Load Recent Scans
        self.load_recent_scans()

        # Debug Lab State (local cache of Pydantic model dump)
        self.debug_report = {}
        self.debug_loading = False
        self.latest_capture_src = None
        # self.was_processing is removed as we use event based updates now
        self.watchdog_counter = 0

        # UI State Persistence
        self.expansion_states = {}

        # Metadata for Filters (Shared with BulkAddPage logic)
        self.metadata = {
            'available_sets': [],
            'available_monster_races': [],
            'available_st_races': [],
            'available_archetypes': [],
            'available_card_types': ['Monster', 'Spell', 'Trap', 'Skill'],
        }

        # Scan View State
        page_size = 50
        self.scan_state = {
            'collection_cards': [], # List[BulkCollectionEntry]
            'collection_filtered': [],
            'collection_page': 1,
            'collection_page_size': page_size,
            'collection_total_pages': 1,
            'search_text': '',
            'sort_by': 'Newest',
            'sort_desc': False,

            # Filters (standard keys for FilterPane)
            'filter_set': '',
            'filter_rarity': '',
            'filter_attr': '',
            'filter_card_type': ['Monster', 'Spell', 'Trap'],
            'filter_monster_race': '',
            'filter_st_race': '',
            'filter_archetype': '',
            'filter_monster_category': [],
            'filter_level': None,
            'filter_atk_min': 0, 'filter_atk_max': 5000,
            'filter_def_min': 0, 'filter_def_max': 5000,
            'filter_price_min': 0.0, 'filter_price_max': 1000.0,
            'filter_ownership_min': 0, 'filter_ownership_max': 100,
            'filter_condition': [], 'filter_owned_lang': '',

             # Metadata linking
            **self.metadata
        }

        # Additional Update Controls State
        self.update_state = {
            'apply_lang': False,
            'apply_cond': False,
            'apply_first': False,
            'apply_storage': False
        }

        self.single_card_view = SingleCardView()
        self.filter_pane = None
        self.filter_dialog = None

    async def init_data(self):
        try:
            # Load DB if needed
            lang_code = config_manager.get_language().lower()
            api_cards = await ygo_service.load_card_database(lang_code)

            # Populate Metadata
            sets = set()
            m_races = set()
            st_races = set()
            archetypes = set()

            for c in api_cards:
                if c.card_sets:
                    for s in c.card_sets:
                        sets.add(f"{s.set_name} | {s.set_code.split('-')[0] if '-' in s.set_code else s.set_code}")
                if c.archetype: archetypes.add(c.archetype)
                if "Monster" in c.type: m_races.add(c.race)
                elif "Spell" in c.type or "Trap" in c.type:
                    if c.race: st_races.add(c.race)

            self.metadata['available_sets'][:] = sorted(list(sets))
            self.metadata['available_monster_races'][:] = sorted(list(m_races))
            self.metadata['available_st_races'][:] = sorted(list(st_races))
            self.metadata['available_archetypes'][:] = sorted(list(archetypes))

            # Update scan_state references to metadata lists (in case they were copied by value, though dicts are ref)
            # Actually **self.metadata unpacking creates copies in the dict. We need to update scan_state.
            for k, v in self.metadata.items():
                self.scan_state[k] = v

            # Refresh Scan View
            self.refresh_scan_view()
            if self.filter_pane: self.filter_pane.update_options()
        except Exception as e:
            logger.error(f"Error initializing data: {e}")

    def refresh_scan_view(self):
        # Build entries
        entries = _build_collection_entries(self.scan_collection)
        self.scan_state['collection_cards'] = entries
        self.apply_scan_filters()

    def apply_scan_filters(self):
        source = self.scan_state['collection_cards']
        res = list(source)
        s = self.scan_state

        txt = s['search_text'].lower()
        if txt:
            def matches(e: BulkCollectionEntry):
                return (txt in e.api_card.name.lower() or
                        txt in e.set_code.lower() or
                        txt in e.api_card.desc.lower())
            res = [e for e in res if matches(e)]

        if s['filter_card_type']: res = [e for e in res if any(t in e.api_card.type for t in s['filter_card_type'])]
        if s['filter_attr']: res = [e for e in res if e.api_card.attribute == s['filter_attr']]
        if s['filter_monster_race']: res = [e for e in res if "Monster" in e.api_card.type and e.api_card.race == s['filter_monster_race']]
        if s['filter_st_race']: res = [e for e in res if ("Spell" in e.api_card.type or "Trap" in e.api_card.type) and e.api_card.race == s['filter_st_race']]
        if s['filter_archetype']: res = [e for e in res if e.api_card.archetype == s['filter_archetype']]
        if s['filter_set']:
             target = s['filter_set'].split('|')[0].strip().lower()
             res = [e for e in res if target in e.set_name.lower() or target in e.set_code.lower()]
        if s['filter_rarity']:
             target = s['filter_rarity'].lower()
             res = [e for e in res if e.rarity.lower() == target]
        if s['filter_monster_category']:
             cats = s['filter_monster_category']
             res = [e for e in res if any(e.api_card.matches_category(cat) for cat in cats)]
        if s['filter_owned_lang']:
             res = [e for e in res if e.language == s['filter_owned_lang']]
        if s['filter_condition']:
             res = [e for e in res if e.condition in s['filter_condition']]

        # Sort
        key = s['sort_by']
        reverse = s['sort_desc']
        if key == 'Name': res.sort(key=lambda x: x.api_card.name, reverse=reverse)
        elif key == 'ATK': res.sort(key=lambda x: (x.api_card.atk or -1), reverse=reverse)
        elif key == 'DEF': res.sort(key=lambda x: (getattr(x.api_card, 'def_', None) or -1), reverse=reverse)
        elif key == 'Level': res.sort(key=lambda x: (x.api_card.level or -1), reverse=reverse)
        elif key == 'Set Code': res.sort(key=lambda x: x.set_code, reverse=reverse)
        elif key == 'Quantity': res.sort(key=lambda x: x.quantity, reverse=reverse)
        elif key == 'Newest':
            # Newest relies on order of addition? Or we can assume order in list is roughly newest if prepended?
            # Or use timestamp? scan_collection doesn't have timestamp per entry explicitly unless we use something else.
            # Assuming scan_collection order is preserved (prepend), then index is proxy for newest.
            # But here we are sorting `res` which is a new list.
            # `BulkCollectionEntry` creation order follows `scan_collection` iteration order.
            # If `scan_collection` has newest first, then default order is newest.
            # But let's verify. `on_card_confirmed` inserts at 0. So yes.
            # So `res` is naturally sorted by Newest (Desc) if we don't shuffle.
            if reverse: # If Desc is True (meaning we want Newest first? usually Newest IS the default order)
                 # If default list is [Newest...Oldest]
                 # If reverse=True, we reverse it to [Oldest...Newest] (Oldest First)
                 # Wait. sort_desc=True usually means Descending order (Largest/Newest first).
                 # If list is already Newest First, then sort_desc=True should keep it.
                 # But we don't have a key to sort by.
                 # We can use index.
                 pass
            else:
                 # If sort_desc=False (Ascending / Oldest First)
                 res.reverse()

        self.scan_state['collection_filtered'] = res
        self.scan_state['collection_page'] = 1
        self.update_scan_pagination()

        # We need to refresh the gallery UI component
        if hasattr(self, 'render_recent_scans_gallery'):
            self.render_recent_scans_gallery.refresh()

    def update_scan_pagination(self):
        count = len(self.scan_state['collection_filtered'])
        self.scan_state['collection_total_pages'] = max(1, (count + self.scan_state['collection_page_size'] - 1) // self.scan_state['collection_page_size'])

    async def reset_scan_filters(self):
        # Reset State
        s = self.scan_state
        s['search_text'] = ''
        s['filter_set'] = ''
        s['filter_rarity'] = ''
        s['filter_attr'] = ''
        s['filter_card_type'] = ['Monster', 'Spell', 'Trap']
        s['filter_monster_race'] = ''
        s['filter_st_race'] = ''
        s['filter_archetype'] = ''
        s['filter_monster_category'] = []
        s['filter_level'] = None
        s['filter_atk_min'] = 0
        s['filter_atk_max'] = 5000
        s['filter_def_min'] = 0
        s['filter_def_max'] = 5000
        s['filter_price_min'] = 0.0
        s['filter_price_max'] = 1000.0
        s['filter_ownership_min'] = 0
        s['filter_ownership_max'] = 100
        s['filter_condition'] = []
        s['filter_owned_lang'] = ''

        # Reset UI
        if self.filter_pane:
            self.filter_pane.reset_ui_elements()

        # Apply
        self.apply_scan_filters()

    def _setup_card_tooltip(self, card: ApiCard, specific_image_id: int = None):
        if not card: return
        target_img = card.card_images[0] if card.card_images else None
        if specific_image_id and card.card_images:
            for img in card.card_images:
                if img.id == specific_image_id:
                    target_img = img
                    break
        if not target_img: return

        img_id = target_img.id
        high_res_url = target_img.image_url
        low_res_url = target_img.image_url_small
        is_local = image_manager.image_exists(img_id, high_res=True)
        initial_src = f"/images/{img_id}_high.jpg" if is_local else (high_res_url or low_res_url)

        with ui.tooltip().classes('bg-transparent shadow-none border-none p-0 overflow-visible z-[9999] max-w-none').props('style="max-width: none" delay=5000') as tooltip:
            if initial_src:
                ui.image(initial_src).classes('w-auto h-[65vh] min-w-[1000px] object-contain rounded-lg shadow-2xl').props('fit=contain')
            if not is_local and high_res_url:
                async def ensure_high():
                    if not image_manager.image_exists(img_id, high_res=True):
                         await image_manager.ensure_image(img_id, high_res_url, high_res=True)
                tooltip.on('show', ensure_high)

    @ui.refreshable
    def render_recent_scans_gallery(self):
        start = (self.scan_state['collection_page'] - 1) * self.scan_state['collection_page_size']
        end = min(start + self.scan_state['collection_page_size'], len(self.scan_state['collection_filtered']))
        items = self.scan_state['collection_filtered'][start:end]

        url_map = {}
        for item in items:
            if item.image_url: url_map[item.image_id] = item.image_url
        if url_map:
            asyncio.create_task(image_manager.download_batch(url_map, concurrency=5))

        if not items:
            ui.label('No scans found.').classes('text-gray-500 italic w-full text-center mt-10')
            return

        with ui.grid(columns='repeat(auto-fill, minmax(110px, 1fr))').classes('w-full gap-2 p-2').props('id="scan-list"'):
            for item in items:
                img_src = f"/images/{item.image_id}.jpg" if image_manager.image_exists(item.image_id) else item.image_url

                cond_short = CONDITION_ABBREVIATIONS.get(item.condition, item.condition[:2].upper())

                with ui.card().classes('p-0 cursor-pointer hover:scale-105 transition-transform border border-accent w-full aspect-[2/3] select-none') \
                        .props(f'data-id="{item.id}"') \
                        .on('click', lambda i=item: self.open_single_view_scan(i)) \
                        .on('contextmenu.prevent', lambda i=item: self.reduce_scan_card_qty(i)):

                    with ui.element('div').classes('relative w-full h-full'):
                         ui.image(img_src).classes('w-full h-full object-cover')

                         lang_code = item.language.strip().upper()
                         country_code = LANGUAGE_COUNTRY_MAP.get(lang_code)
                         if country_code:
                             ui.element('img').props(f'src="https://flagcdn.com/h24/{country_code}.png" alt="{lang_code}"').classes('absolute top-[1px] left-[1px] h-4 w-6 shadow-black drop-shadow-md rounded bg-black/30')
                         else:
                             ui.label(lang_code).classes('absolute top-[1px] left-[1px] text-xs font-bold shadow-black drop-shadow-md bg-black/30 rounded px-1')

                         ui.label(f"{item.quantity}").classes('absolute top-1 right-1 bg-accent text-dark font-bold px-2 rounded-full text-xs shadow-md')

                         with ui.column().classes('absolute bottom-0 left-0 bg-black/80 text-white text-[9px] px-1 gap-0 w-full'):
                             ui.label(item.api_card.name).classes('text-[9px] font-bold text-white leading-none truncate w-full')
                             with ui.row().classes('w-full justify-between items-center'):
                                 with ui.row().classes('gap-1'):
                                     ui.label(cond_short).classes('font-bold text-yellow-500')
                                     if item.first_edition:
                                         ui.label('1st').classes('font-bold text-orange-400')
                                 ui.label(item.set_code).classes('font-mono')
                             with ui.row().classes('w-full justify-between items-center gap-1'):
                                 ui.label(item.rarity).classes('text-[8px] text-gray-300 truncate flex-shrink')
                                 # ui.label(item.storage_location or "None").classes('text-[8px] text-gray-400 font-mono truncate flex-shrink text-right')

                    self._setup_card_tooltip(item.api_card, specific_image_id=item.image_id)

    @ui.refreshable
    def render_recent_scans_panel(self):
        # Header
        with ui.row().classes('w-full p-2 bg-gray-900 border-b border-gray-800 items-center justify-between gap-2 flex-nowrap overflow-x-auto'):
            ui.label('Recent Scans').classes('text-h6 font-bold')

            with ui.row().classes('items-center gap-1 flex-nowrap'):
                # Undo
                ui.button("Undo", icon='undo', on_click=self.on_undo_click).props('flat dense color=white size=sm')

                # Update Controls
                with ui.row().classes('gap-1 items-center bg-gray-800 rounded px-1 border border-gray-700'):
                    ui.button("Update", on_click=self.on_update_all_click).props('flat dense color=warning size=sm')
                    ui.checkbox('Lang', value=self.update_state['apply_lang'],
                                on_change=lambda e: self.update_state.update({'apply_lang': e.value})).props('dense size=xs').classes('text-[10px]')
                    ui.checkbox('Cond', value=self.update_state['apply_cond'],
                                on_change=lambda e: self.update_state.update({'apply_cond': e.value})).props('dense size=xs').classes('text-[10px]')
                    ui.checkbox('1st', value=self.update_state['apply_first'],
                                on_change=lambda e: self.update_state.update({'apply_first': e.value})).props('dense size=xs').classes('text-[10px]')
                    ui.checkbox('Storage', value=self.update_state['apply_storage'],
                                on_change=lambda e: self.update_state.update({'apply_storage': e.value})).props('dense size=xs').classes('text-[10px]')

                ui.button("Remove All", on_click=self.on_remove_all_click).props('flat dense color=negative size=sm')

                ui.separator().props('vertical')

                ui.input(placeholder='Search...',
                         on_change=lambda e: self.apply_scan_filters()) \
                    .bind_value(self.scan_state, 'search_text') \
                    .props('dense borderless dark debounce=300') \
                    .classes('w-32 text-sm')

                ui.separator().props('vertical')

                # Pagination
                async def change_scan_page(delta):
                     new_p = max(1, min(self.scan_state['collection_total_pages'], self.scan_state['collection_page'] + delta))
                     if new_p != self.scan_state['collection_page']:
                         self.scan_state['collection_page'] = new_p
                         self.render_recent_scans_gallery.refresh()

                ui.button(icon='chevron_left', on_click=lambda: change_scan_page(-1)).props('flat dense color=white size=sm')
                ui.label().bind_text_from(self.scan_state, 'collection_page', lambda p: f"{p}/{self.scan_state['collection_total_pages']}").classes('text-xs font-mono')
                ui.button(icon='chevron_right', on_click=lambda: change_scan_page(1)).props('flat dense color=white size=sm')

                ui.separator().props('vertical')

                # Sort
                col_sort_opts = ['Name', 'ATK', 'DEF', 'Level', 'Set Code', 'Quantity', 'Newest']
                async def on_scan_sort(e):
                    self.scan_state['sort_by'] = e.value
                    self.apply_scan_filters()
                ui.select(col_sort_opts, value=self.scan_state['sort_by'], on_change=on_scan_sort).props('dense options-dense borderless').classes('w-20 text-xs')

                async def toggle_scan_sort():
                    self.scan_state['sort_desc'] = not self.scan_state['sort_desc']
                    self.apply_scan_filters()
                ui.button(on_click=toggle_scan_sort).props('flat dense color=white size=sm').bind_icon_from(self.scan_state, 'sort_desc', lambda d: 'arrow_downward' if d else 'arrow_upward')

                if self.filter_dialog:
                     ui.button(icon='filter_list', on_click=self.filter_dialog.open).props('flat dense color=white size=sm')

        with ui.column().classes('w-full flex-grow relative bg-black/20 overflow-hidden'):
             with ui.scroll_area().classes('w-full h-full'):
                self.render_recent_scans_gallery()

    async def on_undo_click(self):
        last_change = changelog_manager.undo_last_change("scan_temp")
        if last_change:
            # Revert logic
            action = last_change.get('action')
            data = last_change.get('card_data')
            qty = last_change.get('quantity', 1)

            if action == 'COMMIT':
                target_name = last_change.get('target_collection')
                changes = last_change.get('changes', [])

                try:
                    target_col = persistence.load_collection(target_name)

                    # Remove from Target
                    for c in changes:
                        api_card = ygo_service.get_card(c['card_data']['card_id'])
                        if api_card:
                            CollectionEditor.apply_change(
                                collection=target_col,
                                api_card=api_card,
                                set_code=c['card_data']['set_code'],
                                rarity=c['card_data']['rarity'],
                                language=c['card_data']['language'],
                                quantity=-c['quantity'], # Remove
                                condition=c['card_data']['condition'],
                                first_edition=c['card_data']['first_edition'],
                                image_id=c['card_data']['image_id'],
                                variant_id=c['card_data']['variant_id'],
                                mode='ADD',
                                storage_location=c['card_data'].get('storage_location')
                            )

                    persistence.save_collection(target_col, target_name)

                    # Restore to Scan Collection
                    for c in changes:
                        api_card = ygo_service.get_card(c['card_data']['card_id'])
                        if api_card:
                            CollectionEditor.apply_change(
                                collection=self.scan_collection,
                                api_card=api_card,
                                set_code=c['card_data']['set_code'],
                                rarity=c['card_data']['rarity'],
                                language=c['card_data']['language'],
                                quantity=c['quantity'], # Add back
                                condition=c['card_data']['condition'],
                                first_edition=c['card_data']['first_edition'],
                                image_id=c['card_data']['image_id'],
                                variant_id=c['card_data']['variant_id'],
                                mode='ADD',
                                storage_location=c['card_data'].get('storage_location')
                            )

                    self.save_recent_scans()
                    self.refresh_scan_view()
                    ui.notify(f"Undid Commit to {target_name}", type='positive')

                except Exception as e:
                    ui.notify(f"Failed to undo commit: {e}", type='negative')

            elif action == 'BATCH':
                # Reverse all changes
                changes = last_change.get('changes', [])
                for c in changes:
                    c_action = c['action']
                    c_qty = c['quantity']
                    c_data = c['card_data']

                    # Reverse action
                    revert_qty = -c_qty if c_action == 'ADD' else c_qty

                    if c_action in ['ADD', 'REMOVE', 'UPDATE']:
                         api_card = ygo_service.get_card(c_data['card_id'])
                         if api_card:
                             CollectionEditor.apply_change(
                                 collection=self.scan_collection,
                                 api_card=api_card,
                                 set_code=c_data['set_code'],
                                 rarity=c_data['rarity'],
                                 language=c_data['language'],
                                 quantity=revert_qty,
                                 condition=c_data['condition'],
                                 first_edition=c_data['first_edition'],
                                 image_id=c_data['image_id'],
                                 variant_id=c_data['variant_id'],
                                 mode='ADD',
                                 storage_location=c_data.get('storage_location')
                             )

                self.save_recent_scans()
                self.refresh_scan_view()
                ui.notify("Undo successful", type='positive')

            else:
                # Single action
                revert_qty = -qty if action == 'ADD' else qty

                api_card = ygo_service.get_card(data['card_id'])
                if api_card:
                    CollectionEditor.apply_change(
                        collection=self.scan_collection,
                        api_card=api_card,
                        set_code=data['set_code'],
                        rarity=data['rarity'],
                        language=data['language'],
                        quantity=revert_qty,
                        condition=data['condition'],
                        first_edition=data['first_edition'],
                        image_id=data['image_id'],
                        variant_id=data['variant_id'],
                        mode='ADD',
                        storage_location=data.get('storage_location')
                    )

            self.save_recent_scans()
            self.refresh_scan_view()
            ui.notify("Undo successful", type='positive')
        else:
            ui.notify("Nothing to undo", type='warning')

    async def on_update_all_click(self):
        filtered = self.scan_state['collection_filtered']
        if not filtered: return

        apply_lang = self.update_state['apply_lang']
        apply_cond = self.update_state['apply_cond']
        apply_first = self.update_state['apply_first']
        apply_storage = self.update_state['apply_storage']

        if not (apply_lang or apply_cond or apply_first or apply_storage):
             ui.notify("Select properties to update", type='warning')
             return

        target_lang = 'EN'
        target_cond = self.default_condition
        target_first = False
        target_storage = None

        processed_changes = []

        for item in filtered:
            new_lang = target_lang if apply_lang else item.language
            new_cond = target_cond if apply_cond else item.condition
            new_first = target_first if apply_first else item.first_edition
            new_storage = target_storage if apply_storage else item.storage_location

            if (new_lang == item.language and new_cond == item.condition and
                new_first == item.first_edition and new_storage == item.storage_location):
                continue

            # Remove Old
            CollectionEditor.apply_change(
                collection=self.scan_collection,
                api_card=item.api_card,
                set_code=item.set_code,
                rarity=item.rarity,
                language=item.language,
                quantity=-item.quantity,
                condition=item.condition,
                first_edition=item.first_edition,
                image_id=item.image_id,
                variant_id=item.variant_id,
                mode='ADD',
                storage_location=item.storage_location
            )

            # Add New
            CollectionEditor.apply_change(
                collection=self.scan_collection,
                api_card=item.api_card,
                set_code=item.set_code,
                rarity=item.rarity,
                language=new_lang,
                quantity=item.quantity,
                condition=new_cond,
                first_edition=new_first,
                image_id=item.image_id,
                variant_id=item.variant_id,
                mode='ADD',
                storage_location=new_storage
            )

            processed_changes.append({
                'action': 'UPDATE',
                'quantity': item.quantity,
                'card_data': {
                     'card_id': item.api_card.id,
                     'set_code': item.set_code,
                     'rarity': item.rarity,
                     'image_id': item.image_id,
                     'variant_id': item.variant_id,
                     'language': new_lang,
                     'condition': new_cond,
                     'first_edition': new_first,
                     'storage_location': new_storage
                }
            })

        if processed_changes:
            self.save_recent_scans()
            changelog_manager.log_batch_change("scan_temp", "Bulk Update", processed_changes)
            self.refresh_scan_view()
            ui.notify(f"Updated {len(processed_changes)} items", type='positive')

    async def on_remove_all_click(self):
        filtered = self.scan_state['collection_filtered']
        if not filtered: return

        processed_changes = []
        for item in filtered:
            CollectionEditor.apply_change(
                collection=self.scan_collection,
                api_card=item.api_card,
                set_code=item.set_code,
                rarity=item.rarity,
                language=item.language,
                quantity=-item.quantity,
                condition=item.condition,
                first_edition=item.first_edition,
                image_id=item.image_id,
                variant_id=item.variant_id,
                mode='ADD',
                storage_location=item.storage_location
            )

            processed_changes.append({
                'action': 'REMOVE',
                'quantity': item.quantity,
                'card_data': {
                     'card_id': item.api_card.id,
                     'set_code': item.set_code,
                     'rarity': item.rarity,
                     'image_id': item.image_id,
                     'variant_id': item.variant_id,
                     'language': item.language,
                     'condition': item.condition,
                     'first_edition': item.first_edition,
                     'storage_location': item.storage_location
                }
            })

        if processed_changes:
            self.save_recent_scans()
            changelog_manager.log_batch_change("scan_temp", "Bulk Remove", processed_changes)
            self.refresh_scan_view()
            ui.notify(f"Removed {len(processed_changes)} items", type='positive')

    async def open_single_view_scan(self, item):
        async def on_save(card, set_code, rarity, language, quantity, condition, first_edition, image_id, variant_id, mode):
             success = CollectionEditor.apply_change(
                 collection=self.scan_collection,
                 api_card=card,
                 set_code=set_code,
                 rarity=rarity,
                 language=language,
                 quantity=quantity,
                 condition=condition,
                 first_edition=first_edition,
                 image_id=image_id,
                 mode=mode,
                 variant_id=variant_id,
                 storage_location=item.storage_location
             )

             if success:
                 self.save_recent_scans()
                 card_data = {
                    'card_id': card.id,
                    'name': card.name,
                    'set_code': set_code,
                    'rarity': rarity,
                    'image_id': image_id,
                    'language': language,
                    'condition': condition,
                    'first_edition': first_edition,
                    'variant_id': variant_id,
                    'storage_location': item.storage_location
                 }
                 changelog_manager.log_change("scan_temp", mode, card_data, quantity)
                 self.refresh_scan_view()
                 ui.notify('Updated.', type='positive')

        await self.single_card_view.open_collectors(
            card=item.api_card,
            owned_count=item.quantity,
            set_code=item.set_code,
            rarity=item.rarity,
            set_name=item.set_name,
            language=item.language,
            condition=item.condition,
            first_edition=item.first_edition,
            image_url=item.image_url,
            image_id=item.image_id,
            set_price=item.price,
            current_collection=self.scan_collection,
            save_callback=on_save,
            variant_id=item.variant_id,
            hide_header_stats=False
        )

    async def reduce_scan_card_qty(self, item):
        CollectionEditor.apply_change(
            collection=self.scan_collection,
            api_card=item.api_card,
            set_code=item.set_code,
            rarity=item.rarity,
            language=item.language,
            quantity=-1,
            condition=item.condition,
            first_edition=item.first_edition,
            image_id=item.image_id,
            variant_id=item.variant_id,
            mode='ADD',
            storage_location=item.storage_location
        )

        self.save_recent_scans()

        card_data = {
            'card_id': item.api_card.id,
            'name': item.api_card.name,
            'set_code': item.set_code,
            'rarity': item.rarity,
            'image_id': item.image_id,
            'language': item.language,
            'condition': item.condition,
            'first_edition': item.first_edition,
            'variant_id': item.variant_id,
            'storage_location': item.storage_location
        }
        changelog_manager.log_change("scan_temp", 'REMOVE', card_data, 1)

        self.refresh_scan_view()
        ui.notify("Removed 1", type='info')

    def save_settings(self):
        """Saves current settings to config."""
        self.config['ocr_tracks'] = [self.selected_track]
        self.config['preprocessing_mode'] = self.preprocessing_mode
        self.config['art_match_yolo'] = self.art_match_yolo
        self.config['ambiguity_threshold'] = self.ambiguity_threshold
        self.config['save_warped_scan'] = self.save_warped_scan
        self.config['save_raw_scan'] = self.save_raw_scan
        self.config['art_match_threshold'] = self.art_match_threshold
        self.config['rotation'] = self.rotation

        # Sync list used by logic
        self.ocr_tracks = [self.selected_track]

        config_manager.save_config(self.config)

    @property
    def scanned_cards(self) -> List[Dict[str, Any]]:
        """Backwards compatibility adapter for old UI code."""
        res = []
        for card in self.scan_collection.cards:
            for var in card.variants:
                for entry in var.entries:
                    item = {
                        'card_id': card.card_id,
                        'name': card.name,
                        'set_code': var.set_code,
                        'rarity': var.rarity,
                        'variant_id': var.variant_id,
                        'image_id': var.image_id,
                        'language': entry.language,
                        'condition': entry.condition,
                        'first_edition': entry.first_edition,
                        # Fake path for UI
                        'image_path': f"data/images/{var.image_id}.jpg" if var.image_id else None
                    }
                    res.append(item)
        # Reverse to show newest first (mimic insert(0))
        return list(reversed(res))

    @scanned_cards.setter
    def scanned_cards(self, value):
        if value == []:
            self.scan_collection.cards = []

    def load_recent_scans(self):
        """Loads scans from temp file."""
        temp_path = "data/scans/scans_temp.json"
        self.scan_collection = Collection(name="scan_temp", cards=[])

        if os.path.exists(temp_path):
            try:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check format
                if isinstance(data, dict) and 'cards' in data:
                    # New Format
                    self.scan_collection = Collection(**data)
                elif isinstance(data, list):
                    # Old Format (List of Dicts) - Migrate
                    self._migrate_legacy_scans(data)
                    self.save_recent_scans() # Save in new format
            except Exception as e:
                logger.error(f"Failed to load recent scans: {e}")

    def _migrate_legacy_scans(self, data: List[Dict]):
        for item in data:
            if not item.get('card_id'): continue

            card_id = item['card_id']
            set_code = item.get('set_code')
            rarity = item.get('rarity')
            variant_id = item.get('variant_id') or str(card_id)
            image_id = item.get('image_id')

            # Find/Create Card
            card = next((c for c in self.scan_collection.cards if c.card_id == card_id), None)
            if not card:
                card = CollectionCard(card_id=card_id, name=item.get('name', 'Unknown'))
                self.scan_collection.cards.append(card)

            # Find/Create Variant
            variant = next((v for v in card.variants if v.variant_id == variant_id), None)
            if not variant:
                 # Try soft match
                 variant = next((v for v in card.variants if v.set_code == set_code and v.rarity == rarity), None)

            if not variant:
                variant = CollectionVariant(
                    variant_id=variant_id,
                    set_code=set_code or "Unknown",
                    rarity=rarity or "Common",
                    image_id=image_id
                )
                card.variants.append(variant)

            entry = CollectionEntry(
                condition=item.get('condition', self.default_condition),
                language=item.get('language', 'EN'),
                first_edition=item.get('first_edition', False),
                quantity=1
            )
            variant.entries.append(entry)

    def save_recent_scans(self):
        """Saves current scanned cards to temp file."""
        temp_path = "data/scans/scans_temp.json"
        try:
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            data = self.scan_collection.model_dump(mode='json')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save recent scans: {e}")

    async def init_cameras(self):
        try:
            js_loaded = await ui.run_javascript('window.scanner_js_loaded', timeout=5.0)
            if not js_loaded: return
            devices = await ui.run_javascript('getVideoDevices()')
            if devices and self.camera_select:
                self.camera_select.options = {d['value']: d['label'] for d in devices}
                if not self.camera_select.value and devices:
                    self.camera_select.value = devices[0]['value']
        except: pass

    def on_scanner_event(self, event):
        """Callback for scanner events."""
        if not self.is_active: return

        # Push state immediately
        if event.snapshot:
            self.debug_report = event.snapshot.model_dump()
        self.event_queue.put(event)

    def on_card_confirmed(self, result_dict: Dict[str, Any]):
        """Callback from Ambiguity Dialog or direct addition."""

        # Save Warped Image logic
        if self.save_warped_scan and result_dict.get('scan_image_path') and result_dict.get('card_id'):
            try:
                src_path = result_dict['scan_image_path']
                if os.path.exists(src_path):
                    target_dir = "data/scans/card_images"
                    os.makedirs(target_dir, exist_ok=True)

                    card_id = result_dict['card_id']
                    base_name = str(card_id)
                    ext = ".jpg"
                    target_path = os.path.join(target_dir, f"{base_name}{ext}")

                    # Handle collisions
                    counter = 1
                    while os.path.exists(target_path):
                        target_path = os.path.join(target_dir, f"{base_name}({counter}){ext}")
                        counter += 1

                    shutil.copy2(src_path, target_path)
                    logger.info(f"Saved scan image to {target_path}")
            except Exception as e:
                logger.error(f"Failed to save warped scan image: {e}")

        # Save Raw Image logic
        if self.save_raw_scan and result_dict.get('raw_image_path') and result_dict.get('card_id'):
             try:
                src_path = result_dict['raw_image_path']
                if os.path.exists(src_path):
                    target_dir = "data/scans/raw_images"
                    os.makedirs(target_dir, exist_ok=True)

                    card_id = result_dict['card_id']
                    base_name = str(card_id)
                    ext = ".jpg"
                    target_path = os.path.join(target_dir, f"{base_name}{ext}")

                    # Handle collisions
                    counter = 1
                    while os.path.exists(target_path):
                        target_path = os.path.join(target_dir, f"{base_name}({counter}){ext}")
                        counter += 1

                    shutil.copy2(src_path, target_path)
                    logger.info(f"Saved raw scan image to {target_path}")
             except Exception as e:
                logger.error(f"Failed to save raw scan image: {e}")

        # Cleanup temp raw file
        if result_dict.get('raw_image_path') and os.path.exists(result_dict['raw_image_path']):
             try:
                 os.remove(result_dict['raw_image_path'])
             except: pass

        # Add to Collection
        card_id = result_dict['card_id']
        api_card = ygo_service.get_card(card_id)
        if not api_card:
            ui.notify(f"Error: Card {card_id} not found in DB", type='negative')
            return

        set_code = result_dict.get('set_code')
        rarity = result_dict.get('rarity')
        variant_id = result_dict.get('variant_id')
        image_id = result_dict.get('image_id')
        language = result_dict.get('language', 'EN')
        condition = result_dict.get('condition', self.default_condition)
        first_edition = result_dict.get('first_edition', False)

        # Generate variant_id if missing (essential for log consistency)
        if not variant_id:
             variant_id = generate_variant_id(card_id, set_code, rarity, image_id)

        CollectionEditor.apply_change(
            collection=self.scan_collection,
            api_card=api_card,
            set_code=set_code,
            rarity=rarity,
            language=language,
            quantity=1,
            condition=condition,
            first_edition=first_edition,
            image_id=image_id,
            variant_id=variant_id,
            mode='ADD',
            storage_location=None
        )

        self.save_recent_scans()

        # Log Change
        card_data = {
            'card_id': card_id,
            'name': api_card.name,
            'set_code': set_code,
            'rarity': rarity,
            'image_id': image_id,
            'language': language,
            'condition': condition,
            'first_edition': first_edition,
            'variant_id': variant_id
        }
        changelog_manager.log_change("scan_temp", 'ADD', card_data, 1)

        self.refresh_scan_view()
        ui.notify(f"Added: {result_dict.get('name')}", type='positive')

    async def event_consumer(self):
        """Consumes events from the local queue and updates UI."""
        try:
            # Drive the matching process
            await scanner_service.scanner_manager.process_pending_lookups()

            # 1. Process Queued Events (Fast path)
            while not self.event_queue.empty():
                try:
                    event = self.event_queue.get_nowait()

                    # Apply snapshot
                    if event.snapshot:
                        self.debug_report = event.snapshot.model_dump()

                    # Refresh logic based on event type
                    if event.type in ['status_update', 'scan_queued', 'scan_started', 'step_complete', 'scan_finished']:

                        # Clear local capture preview once the backend has initialized the new scan (showing the real rotated image)
                        if event.type == 'step_complete' and event.data.get('step') == 'init':
                            self.latest_capture_src = None

                        self.refresh_debug_ui()

                        # Handle specific finished notifications
                        if event.type == 'scan_finished':
                            if not event.data.get('success'):
                                ui.notify(f"Scan Failed: {event.data.get('error', 'Unknown')}", type='negative')

                    if event.type == 'error':
                        ui.notify(event.data.get('message', 'Error'), type='negative')

                except queue.Empty:
                    break

            # 2. Watchdog / Polling fallback (Robustness)
            # Every 10 ticks (approx 1 sec), force fetch the state
            self.watchdog_counter += 1
            if self.watchdog_counter >= 10:
                self.watchdog_counter = 0
                snapshot = scanner_service.scanner_manager.get_debug_snapshot()
                if snapshot and snapshot != self.debug_report:
                    self.debug_report = snapshot
                    self.refresh_debug_ui()

            # 3. Check result queue
            res = scanner_service.scanner_manager.get_latest_result()
            if res:
                logger.info(f"UI Received Result: {res.get('set_code')}, Ambiguous: {res.get('ambiguity_flag')}")

                # Check for empty candidates (No Match)
                if not res.get('candidates'):
                    ui.notify("No match found", type='negative')

                elif res.get('ambiguity_flag'):
                    ui.notify("Scan Ambiguous: Please resolve.", type='warning', timeout=5000)
                    dialog = AmbiguityDialog(res, self.on_card_confirmed)
                    dialog.open()
                else:
                    ui.notify("Scan Successful!", type='positive', timeout=3000)
                    self.on_card_confirmed(res)

                self.refresh_debug_ui() # Ensure final result is shown

        except Exception as e:
            logger.error(f"Error in event_consumer: {e}")

    async def start_camera(self):
        device_id = self.camera_select.value if self.camera_select else None
        try:
            if await ui.run_javascript(f'startCamera("{device_id}")', timeout=20.0):
                # We don't need to start/stop the manager here anymore, it runs daemon
                # Use dynamic import access
                scanner_service.scanner_manager.start()
                self.start_btn.visible = False
                self.stop_btn.visible = True
            else:
                 ui.notify("Failed to start camera (JS returned false)", type='negative')
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            ui.notify(f"Error starting camera: {e}", type='negative')

    async def stop_camera(self):
        await ui.run_javascript('stopCamera()')
        # We no longer stop the manager when camera stops. It runs in background.
        # scanner_service.scanner_manager.stop()
        self.start_btn.visible = True
        self.stop_btn.visible = False

    def remove_card(self, index):
        if 0 <= index < len(self.scanned_cards):
            self.scanned_cards.pop(index)
            self.save_recent_scans()
            self.render_live_list.refresh()

    async def commit_cards(self):
        if not self.target_collection_file:
            ui.notify("Please select a target collection.", type='warning')
            return

        if not self.scan_collection.cards:
            ui.notify("No cards to add.", type='warning')
            return

        try:
            target_col_name = self.target_collection_file
            target_col = persistence.load_collection(target_col_name)

            # Prepare data for transfer and logging
            items_to_move = _build_collection_entries(self.scan_collection)

            changes_for_target = []

            for item in items_to_move:
                CollectionEditor.apply_change(
                    collection=target_col,
                    api_card=item.api_card,
                    set_code=item.set_code,
                    rarity=item.rarity,
                    language=item.language,
                    quantity=item.quantity,
                    condition=item.condition,
                    first_edition=item.first_edition,
                    image_id=item.image_id,
                    variant_id=item.variant_id,
                    mode='ADD',
                    storage_location=item.storage_location
                )

                changes_for_target.append({
                    'action': 'ADD',
                    'quantity': item.quantity,
                    'card_data': {
                        'card_id': item.api_card.id,
                        'name': item.api_card.name,
                        'set_code': item.set_code,
                        'rarity': item.rarity,
                        'image_id': item.image_id,
                        'variant_id': item.variant_id,
                        'language': item.language,
                        'condition': item.condition,
                        'first_edition': item.first_edition,
                        'storage_location': item.storage_location
                    }
                })

            # Save Target
            persistence.save_collection(target_col, target_col_name)

            # Log to Target
            changelog_manager.log_batch_change(target_col_name, "Added from Live Scan", changes_for_target)

            # Log to Scan Temp (Special COMMIT action for Undo)
            changelog_manager._write_entry("scan_temp", {
                "action": "COMMIT",
                "target_collection": target_col_name,
                "changes": changes_for_target,
                "type": "commit"
            })

            # Clear Scan Collection
            self.scan_collection.cards = []
            self.save_recent_scans()

            self.refresh_scan_view()
            ui.notify(f"Added {len(items_to_move)} items to {target_col.name}", type='positive')

        except Exception as e:
            logger.error(f"Error committing cards: {e}")
            ui.notify(f"Error committing cards: {e}", type='negative')

    async def trigger_live_scan(self):
        """Triggers a scan from the Live Tab using current settings."""
        try:
            # Ensure scanner is running (unpause if needed)
            if scanner_service.scanner_manager.is_paused():
                scanner_service.scanner_manager.resume()

            data_url = await ui.run_javascript('captureSingleFrame()')
            if not data_url:
                ui.notify("Camera not active or ready", type='warning')
                return

            header, encoded = data_url.split(",", 1)
            content = base64.b64decode(encoded)

            options = {
                "tracks": [self.selected_track], # Use the single selected track
                "preprocessing": self.preprocessing_mode,
                "art_match_yolo": self.art_match_yolo,
                "ambiguity_threshold": self.ambiguity_threshold,
                "save_warped_scan": self.save_warped_scan,
                "save_raw_scan": self.save_raw_scan,
                "art_match_threshold": self.art_match_threshold,
                "rotation": self.rotation
            }
            fname = f"scan_{int(time.time())}_{uuid.uuid4().hex[:6]}.jpg"
            # Use dynamic import access
            scanner_service.scanner_manager.submit_scan(content, options, label="Live Scan", filename=fname)
            ui.notify("Captured to Queue", type='positive')
        except Exception as e:
            ui.notify(f"Capture failed: {e}", type='negative')

    def refresh_debug_ui(self):
        self.render_debug_results.refresh()
        self.render_debug_analysis.refresh()
        self.render_debug_pipeline_results.refresh()
        self.render_scan_queue.refresh()
        self.render_status_controls.refresh()

    async def handle_debug_upload(self, e: events.UploadEventArguments):
        self.latest_capture_src = None
        try:
            # Handle NiceGUI version differences
            file_obj = getattr(e, 'content', getattr(e, 'file', None))
            if not file_obj:
                raise ValueError("No file content found in event")

            content = await file_obj.read()

            # Extract filename safely
            filename = getattr(e, 'name', None)
            if not filename and hasattr(file_obj, 'name'):
                filename = file_obj.name
            if not filename:
                filename = "upload.jpg"

            options = {
                "tracks": [self.selected_track],
                "preprocessing": self.preprocessing_mode,
                "art_match_yolo": self.art_match_yolo,
                "ambiguity_threshold": self.ambiguity_threshold,
                "save_warped_scan": self.save_warped_scan,
                "art_match_threshold": self.art_match_threshold,
                "rotation": 0 # Explicitly 0 for uploads
            }
            # Use dynamic import access
            scanner_service.scanner_manager.submit_scan(content, options, label="Image Upload", filename=filename)
            ui.notify(f"Queued: {filename}", type='positive')
        except Exception as err:
            ui.notify(f"Upload failed: {err}", type='negative')
        # refresh triggered by event

    async def handle_debug_capture(self):
        # refresh triggered by event
        try:
            # Ensure scanner is running (unpause if needed)
            if scanner_service.scanner_manager.is_paused():
                scanner_service.scanner_manager.resume()

            data_url = await ui.run_javascript('captureSingleFrame()')
            if not data_url:
                ui.notify("Camera not active or ready", type='warning')
                return

            # Decode raw capture
            header, encoded = data_url.split(",", 1)
            content = base64.b64decode(encoded)

            # Create rotated preview locally if needed
            if self.rotation != 0:
                try:
                    img = Image.open(io.BytesIO(content))
                    # Map User Rotation (CW) to PIL Transpose
                    if self.rotation == 90:
                        img = img.transpose(Image.ROTATE_270)
                    elif self.rotation == 180:
                        img = img.transpose(Image.ROTATE_180)
                    elif self.rotation == 270:
                        img = img.transpose(Image.ROTATE_90)

                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    rotated_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    self.latest_capture_src = f"data:image/jpeg;base64,{rotated_b64}"
                except Exception as e:
                    logger.error(f"Failed to rotate preview: {e}")
                    self.latest_capture_src = data_url
            else:
                self.latest_capture_src = data_url

            # We want to show the capture immediately?
            # Yes, locally.
            self.refresh_debug_ui()

            options = {
                "tracks": [self.selected_track],
                "preprocessing": self.preprocessing_mode,
                "art_match_yolo": self.art_match_yolo,
                "ambiguity_threshold": self.ambiguity_threshold,
                "save_warped_scan": self.save_warped_scan,
                "art_match_threshold": self.art_match_threshold,
                "rotation": self.rotation
            }
            fname = f"capture_{int(time.time())}_{uuid.uuid4().hex[:6]}.jpg"
            # Use dynamic import access
            scanner_service.scanner_manager.submit_scan(content, options, label="Camera Capture", filename=fname)
            ui.notify("Capture queued", type='positive')

        except Exception as err:
            ui.notify(f"Capture failed: {err}", type='negative')

    @ui.refreshable
    def render_live_list(self):
        if not self.scanned_cards:
            ui.label("No cards scanned.").classes('text-gray-400 italic')
            return

        for i, card in enumerate(self.scanned_cards):
            with ui.card().classes('w-full mb-2 p-2 flex flex-row items-center gap-4'):
                if card.get('image_path'):
                    ui.image(f"/images/{os.path.basename(card['image_path'])}").classes('w-12 h-16 object-contain')
                with ui.column().classes('flex-grow'):
                    ui.label(card.get('name', 'Unknown')).classes('font-bold')
                    ui.label(f"{card.get('set_code')}").classes('text-xs text-gray-500')

                ui.button(icon='delete', color='negative',
                          on_click=lambda idx=i: self.remove_card(idx)).props('flat')

    @ui.refreshable
    def render_debug_results(self):
        if self.debug_loading:
            ui.spinner(size='lg')
            return

        preview_src = self.latest_capture_src or self.debug_report.get('captured_image_url') or self.debug_report.get('input_image_url')
        if preview_src:
            ui.label("Latest Capture:").classes('font-bold mt-2 text-lg')
            ui.image(preview_src).classes('w-full h-auto border rounded shadow-md')
        elif scanner_service.scanner_manager.is_processing:
             ui.spinner()

    @ui.refreshable
    def render_debug_analysis(self):
        if self.debug_report.get('warped_image_url'):
            ui.label("Perspective Warp:").classes('font-bold text-lg')
            ui.image(self.debug_report['warped_image_url']).classes('w-full h-auto border rounded mb-2')
        else:
            ui.label("Waiting for input...").classes('text-gray-500 italic')

        if self.debug_report.get('roi_viz_url'):
            ui.label("Regions of Interest:").classes('font-bold text-lg')
            ui.image(self.debug_report['roi_viz_url']).classes('w-full h-auto border rounded mb-2')

        art_match = self.debug_report.get('art_match_yolo')
        if art_match:
             ui.separator().classes('my-2')
             ui.label("Art Match (YOLO):").classes('font-bold text-lg text-purple-400')
             with ui.row().classes('items-center gap-2'):
                 ui.label(f"{art_match.get('filename')}").classes('font-bold')
                 ui.badge(f"{art_match.get('score', 0):.3f}", color='purple')

             if art_match.get('image_url'):
                 ui.image(art_match['image_url']).classes('w-full h-auto border rounded border-purple-500 mb-2')

    @ui.refreshable
    def render_debug_pipeline_results(self):
        # Match Candidates (Moved to Top)
        candidates = self.debug_report.get('match_candidates', [])

        # Header Stats
        with ui.row().classes('w-full items-center justify-between mb-2'):
            ui.label("3. OCR & Match Results").classes('text-2xl font-bold text-primary')

            # Show Detected Features prominently
            with ui.row().classes('gap-4'):
                # 1st Edition Status
                is_first_ed = self.debug_report.get('first_edition', False)
                color = 'green' if is_first_ed else 'gray'
                ui.badge(f"1st Ed: {'YES' if is_first_ed else 'NO'}", color=color).classes('text-sm')

                # Visual Rarity
                vis_rarity = self.debug_report.get('visual_rarity', 'Unknown')
                ui.badge(f"Visual: {vis_rarity}", color='blue').classes('text-sm')

                # Card Type
                card_type = self.debug_report.get('card_type')
                if card_type:
                    color = 'purple' if 'TRAP' in card_type.upper() else 'green'
                    ui.badge(f"Type: {card_type}", color=color).classes('text-sm')

        if candidates:
            with ui.card().classes('w-full bg-gray-900 border border-gray-600 p-2 mb-4'):
                ui.label("Match Candidates (Top 10)").classes('font-bold text-lg mb-2')

                # Header
                with ui.grid(columns=5).classes('w-full gap-2 border-b border-gray-600 pb-1 mb-1'):
                    ui.label("Name").classes('font-bold text-xs text-gray-400 col-span-2')
                    ui.label("Set").classes('font-bold text-xs text-gray-400')
                    ui.label("Rarity").classes('font-bold text-xs text-gray-400')
                    ui.label("Score").classes('font-bold text-xs text-gray-400 text-right')

                # Rows
                for c in candidates:
                    with ui.grid(columns=5).classes('w-full gap-2 items-center hover:bg-gray-800 p-1 rounded'):
                        ui.label(c.get('name', '')).classes('text-xs break-all leading-tight col-span-2')
                        ui.label(c.get('set_code', '')).classes('text-xs font-mono text-green-300')
                        ui.label(c.get('rarity', '')).classes('text-xs truncate text-blue-300')
                        ui.label(f"{c.get('score', 0):.1f}").classes('text-xs font-mono text-yellow-400 text-right')
        else:
            ui.label("No Match Candidates Found").classes('text-gray-500 italic mb-4')

        # 4 Collapsable Zones
        def render_zone(title, key):
            data = self.debug_report.get(key)
            # Use persistent state for expansion
            is_open = self.expansion_states.get(key, False) # Default closed to reduce clutter
            with ui.expansion(title, icon='visibility', value=is_open, on_value_change=lambda e: self.expansion_states.__setitem__(key, e.value)).classes('w-full bg-gray-800 border border-gray-600 mb-2'):
                if data:
                    with ui.column().classes('p-2 w-full'):
                        ui.label(f"Set ID: {data.get('set_id', 'N/A')}").classes('font-bold text-green-400')
                        if data.get('card_name'):
                             ui.label(f"Name: {data.get('card_name')}").classes('font-bold text-blue-400')
                        ui.label(f"Conf: {data.get('set_id_conf', 0):.1f}%").classes('text-sm')
                        ui.label(f"Lang: {data.get('language', 'N/A')}").classes('text-sm')
                        ui.separator().classes('bg-gray-600 my-1')
                        ui.label("Raw Text:").classes('text-xs text-gray-400')
                        ui.label(data.get('raw_text', '')).classes('font-mono text-xs break-all bg-black p-1 rounded')
                else:
                    ui.label("No Data").classes('italic text-gray-500 p-2')

        render_zone("Track 1: EasyOCR (Full Frame)", "t1_full")
        render_zone("Track 1: EasyOCR (Cropped)", "t1_crop")
        render_zone("Track 2: DocTR (Full Frame)", "t2_full")
        render_zone("Track 2: DocTR (Cropped)", "t2_crop")

        ui.separator().classes('my-4')

        ui.label("Execution Log:").classes('font-bold text-lg')
        logs = self.debug_report.get('logs', [])
        with ui.scroll_area().classes('h-48 border border-gray-600 p-2 bg-black rounded font-mono text-xs text-green-500'):
            for log in logs:
                ui.label(log)

    @ui.refreshable
    def render_scan_queue(self):
        # Use dynamic import access
        queue_items = scanner_service.scanner_manager.get_queue_snapshot()

        with ui.card().classes('w-full border border-gray-600 rounded p-0'):
             with ui.row().classes('w-full bg-gray-800 p-2 items-center'):
                 ui.icon('list', color='primary')
                 ui.label(f"Scan Queue ({len(queue_items)})").classes('font-bold')

             if not queue_items:
                 ui.label("Queue is empty.").classes('p-4 text-gray-500 italic')
             else:
                 with ui.column().classes('w-full gap-1 p-2'):
                     for i, item in enumerate(queue_items):
                         with ui.row().classes('w-full items-center justify-between bg-gray-800 p-2 rounded border border-gray-700'):
                             with ui.column().classes('gap-0'):
                                 ui.label(item.get('filename') or item.get('type')).classes('text-sm font-bold')
                                 ui.label(time.strftime("%H:%M:%S", time.localtime(item['timestamp']))).classes('text-xs text-gray-400')
                             ui.button(icon='delete', color='negative',
                                       on_click=lambda idx=i: self.delete_queue_item(idx)).props('flat size=sm')

    def delete_queue_item(self, index):
        scanner_service.scanner_manager.remove_scan_request(index)
        self.render_scan_queue.refresh()

    @ui.refreshable
    def render_status_controls(self):
        # Use dynamic import access
        mgr = scanner_service.scanner_manager
        status = mgr.get_status()
        is_paused = mgr.is_paused()

        with ui.row().classes('w-full items-center justify-between bg-gray-800 p-2 rounded border border-gray-700'):
            with ui.row().classes('items-center gap-2'):
                if status == "Processing...":
                    ui.spinner(size='sm')
                elif is_paused:
                    ui.icon('pause_circle', color='warning').classes('text-xl')
                else:
                    ui.icon('play_circle', color='positive').classes('text-xl')

                label_text = status
                if is_paused and status == "Stopped":
                     label_text = "Ready to Start"
                elif is_paused:
                     label_text = "Paused"

                # Transient states
                if not is_paused and status == "Paused":
                    label_text = "Resuming..."
                elif is_paused and status not in ["Paused", "Stopped"]:
                    label_text = "Pausing..."

                with ui.column().classes('gap-0'):
                    ui.label(f"Status: {label_text}").classes('font-bold')
                    ui.label(f"Mgr: {getattr(mgr, 'instance_id', 'N/A')}").classes('text-[10px] text-gray-600')
                    # Access current_step safely from debug_report (it's a dict now in UI context)
                    current_step = self.debug_report.get('current_step', 'Idle')
                    if mgr.is_processing:
                        ui.label(f"{current_step}").classes('text-xs text-blue-400')

            # Controls
            if is_paused:
                 ui.button('Start Processing', icon='play_arrow', color='positive', on_click=self.toggle_pause).props('size=sm')
            else:
                 ui.button('Pause', icon='pause', color='warning', on_click=self.toggle_pause).props('size=sm')

    def toggle_pause(self):
        scanner_service.scanner_manager.toggle_pause()
        self.render_status_controls.refresh()

    def render_debug_lab(self):
        with ui.grid().classes('grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full'):

            # --- CARD 1: CONTROLS & INPUT ---
            with ui.card().classes('w-full p-4 flex flex-col gap-4 shadow-lg bg-gray-900 border border-gray-700'):
                ui.label("1. Configuration & Input").classes('text-2xl font-bold text-primary')
                self.render_status_controls()

                # Configuration Section
                ui.label("Scanner Configuration").classes('font-bold text-lg mt-2')

                # Preprocessing Toggle
                ui.label("Preprocessing Strategy:").classes('font-bold text-gray-300 text-sm')
                with ui.row():
                    ui.radio(['classic', 'classic_white_bg', 'yolo', 'yolo26'], value=self.preprocessing_mode,
                            on_change=lambda e: (setattr(self, 'preprocessing_mode', e.value), self.save_settings())).props('inline')

                # Rotation
                ui.label("Camera Rotation:").classes('font-bold text-gray-300 text-sm')
                with ui.row():
                    ui.toggle({0: '0°', 90: '90°', 180: '180°', 270: '270°'}, value=self.rotation,
                            on_change=lambda e: (setattr(self, 'rotation', e.value), self.save_settings(), ui.run_javascript(f'setRotation({e.value})'))).props('toggle-color=accent')

                # Art Match
                with ui.row().classes('items-center justify-between w-full'):
                    ui.label("Art Style Match (YOLO):").classes('font-bold text-gray-300 text-sm')
                    with ui.row().classes('items-center gap-2'):
                         ui.button('Index Images', icon='refresh', on_click=lambda: scanner_service.scanner_manager.rebuild_art_index(force=True)).props('dense color=purple').tooltip("Rebuild Art Index from data/images")
                         ui.switch(value=self.art_match_yolo,
                                  on_change=lambda e: (setattr(self, 'art_match_yolo', e.value), self.save_settings())).props('color=purple')

                # Tracks Selector (Radio)
                ui.label("Active Track:").classes('font-bold text-gray-300 text-sm')
                ui.radio(['easyocr', 'doctr'], value=self.selected_track,
                        on_change=lambda e: (setattr(self, 'selected_track', e.value), self.save_settings())).props('inline')

                # Ambiguity Threshold
                ui.label("Ambiguity Threshold:").classes('font-bold text-gray-300 text-sm')
                ui.number(value=self.ambiguity_threshold, min=0, max=100, step=1.0,
                         on_change=lambda e: (setattr(self, 'ambiguity_threshold', e.value), self.save_settings())).classes('w-full')

                # Art Match Threshold
                ui.label("Art Match Threshold:").classes('font-bold text-gray-300 text-sm')
                ui.number(value=self.art_match_threshold, min=0, max=1.0, step=0.01,
                         on_change=lambda e: (setattr(self, 'art_match_threshold', e.value), self.save_settings())).classes('w-full')

                # Save Warped Scan
                ui.switch("Save Warped Scans", value=self.save_warped_scan,
                          on_change=lambda e: (setattr(self, 'save_warped_scan', e.value), self.save_settings())).props('color=secondary').classes('w-full')

                # Save Raw Scan
                ui.switch("Save Raw Scans", value=self.save_raw_scan,
                          on_change=lambda e: (setattr(self, 'save_raw_scan', e.value), self.save_settings())).props('color=secondary').classes('w-full')

                # Camera Preview
                ui.label("Camera Preview").classes('font-bold text-lg mt-4')
                with ui.element('div').classes('w-full aspect-video bg-black rounded relative overflow-hidden'):
                    ui.html('<video id="debug-video" autoplay playsinline muted style="width: 100%; height: 100%; object-fit: contain;"></video>', sanitize=False)

                # Controls
                with ui.row().classes('w-full gap-2'):
                    ui.button("Capture & Analyze", on_click=self.handle_debug_capture, icon='camera_alt').classes('flex-grow bg-accent text-black font-bold')

                ui.separator().classes('bg-gray-600')
                ui.upload(label="Upload Image", on_upload=self.handle_debug_upload, auto_upload=True).props('accept=.jpg,.png color=secondary').classes('w-full')

                self.render_scan_queue()
                self.render_debug_results()

            # --- CARD 2: VISUAL ---
            with ui.card().classes('w-full p-4 flex flex-col gap-4 shadow-lg bg-gray-900 border border-gray-700'):
                ui.label("2. Visual Analysis").classes('text-2xl font-bold text-primary')
                self.render_debug_analysis()

            # --- CARD 3: RESULTS ---
            with ui.card().classes('w-full p-4 flex flex-col gap-4 shadow-lg bg-gray-900 border border-gray-700'):
                self.render_debug_pipeline_results()

        ui.run_javascript('initDebugStream()')
        ui.run_javascript(f'setRotation({self.rotation})')

    def toggle_track(self, track, enabled):
        # Deprecated logic in favor of single selection radio
        pass

def scan_page():
    page = ScanPage()

    # Initialize event queue for this page instance
    page.event_queue = queue.Queue()

    def cleanup():
        # Unregister listener
        scanner_service.scanner_manager.unregister_listener(page.on_scanner_event)
        page.is_active = False

    app.on_disconnect(cleanup)

    # Register listener
    scanner_service.scanner_manager.register_listener(page.on_scanner_event)

    # Ensure scanner service is running (idempotent)
    # Use dynamic import access
    scanner_service.scanner_manager.start()
    page.is_active = True

    if not SCANNER_AVAILABLE:
        ui.label("Scanner dependencies not found.").classes('text-red-500 text-xl font-bold')
        return

    ui.add_head_html(JS_CAMERA_CODE)

    def handle_tab_change(e):
        if e.value == 'Live Scan':
            ui.run_javascript('reattachScannerVideo()')
        elif e.value == 'Debug Lab':
            ui.run_javascript('initDebugStream()')

        # Re-apply rotation on tab change to ensure video element has correct style
        ui.run_javascript(f'setRotation({page.rotation})')

    with ui.tabs(on_change=handle_tab_change).classes('w-full') as tabs:
        live_tab = ui.tab('Live Scan')
        debug_tab = ui.tab('Debug Lab')

    with ui.tab_panels(tabs, value=live_tab).classes('w-full h-full p-0'):

        # --- TAB 1: LIVE SCAN ---
        with ui.tab_panel(live_tab).classes('h-full flex flex-col p-2'):
            # --- TOP BAR ---
            with ui.row().classes('w-full items-center gap-4 mb-2 justify-between'):
                # Left: Target Collection
                async def on_target_change(e):
                    page.target_collection_file = e.value
                    # Load collection logic if needed for storage options
                    if page.target_collection_file:
                        try:
                            page.target_collection_obj = persistence.load_collection(page.target_collection_file)
                            if page.storage_select:
                                opts = {None: 'None'}
                                for s in page.target_collection_obj.storage_definitions:
                                    opts[s.name] = s.name
                                page.storage_select.options = opts
                                page.storage_select.update()
                        except: pass

                if page.collections:
                    ui.select(options=page.collections, value=page.target_collection_file, label='Target Collection',
                              on_change=on_target_change).classes('w-64')

                # Right: Defaults & Commit
                with ui.row().classes('items-center gap-2'):
                    ui.label('DEFAULTS:').classes('text-xs font-bold text-gray-400')

                    ui.select(['EN', 'DE', 'FR', 'IT', 'ES', 'PT', 'JP', 'KR'], label='Lang',
                              value=page.default_language,
                              on_change=lambda e: setattr(page, 'default_language', e.value)).props('dense options-dense').classes('w-20')

                    ui.select(options=CARD_CONDITIONS,
                              value=page.default_condition, label="Cond",
                              on_change=lambda e: setattr(page, 'default_condition', e.value)).props('dense options-dense').classes('w-32')

                    page.storage_select = ui.select(options={None: 'None'}, label='Storage',
                                                    value=page.default_storage,
                                                    on_change=lambda e: setattr(page, 'default_storage', e.value)).props('dense options-dense').classes('w-32')

                    # Trigger load once to populate storage
                    if page.target_collection_file:
                         on_target_change(type('obj', (object,), {'value': page.target_collection_file}))

                    ui.button('COMMIT', on_click=page.commit_cards).props('color=positive icon=save')

            # --- MAIN CONTENT ---
            with ui.row().classes('w-full flex-grow gap-4'):
                # LEFT COLUMN (Camera)
                with ui.column().classes('w-1/2 h-full flex flex-col gap-2'):
                    # Camera Controls
                    with ui.card().classes('w-full p-2 bg-gray-900 border border-gray-700'):
                        with ui.row().classes('w-full gap-2 items-center'):
                             page.camera_select = ui.select(options={}, label='Camera').classes('flex-grow')
                             page.start_btn = ui.button('START CAMERA', on_click=page.start_camera).props('icon=videocam')
                             page.stop_btn = ui.button('STOP', on_click=page.stop_camera).props('icon=videocam_off color=negative')
                             page.stop_btn.visible = False

                    # Status Bar
                    page.render_status_controls()

                    # Video
                    with ui.card().classes('w-full flex-grow p-0 overflow-hidden relative bg-black border border-gray-700'):
                        ui.html('<video id="scanner-video" autoplay playsinline muted style="width: 100%; height: 100%; object-fit: contain;"></video>', sanitize=False)
                        ui.html('<canvas id="overlay-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>', sanitize=False)

                    # Capture Button
                    ui.button('CAPTURE & SCAN', on_click=page.trigger_live_scan).classes('w-full py-4 text-lg font-bold').props('color=accent text-color=black icon=camera_alt')

                # RIGHT COLUMN (Recent Scans)
                with ui.column().classes('w-1/2 h-full'):
                    page.filter_dialog = ui.dialog().props('position=right')
                    with page.filter_dialog, ui.card().classes('h-full w-96 bg-gray-900 border-l border-gray-700 p-0 flex flex-col'):
                         with ui.scroll_area().classes('flex-grow w-full'):
                             page.filter_pane = FilterPane(page.scan_state, page.apply_scan_filters, page.reset_scan_filters)
                             page.filter_pane.build()

                    page.render_recent_scans_panel()

        # --- TAB 2: DEBUG LAB ---
        with ui.tab_panel(debug_tab):
             page.render_debug_lab()

    ui.timer(0.1, page.init_data, once=True)
    ui.timer(1.0, page.init_cameras, once=True)

    # Use fast consumer loop instead of slow polling
    ui.timer(0.1, page.event_consumer)

    # Initialize from current state immediately
    page.debug_report = scanner_service.scanner_manager.get_debug_snapshot()
