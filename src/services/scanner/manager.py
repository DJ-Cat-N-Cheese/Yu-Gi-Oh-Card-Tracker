import logging
import threading
import queue
import time
import base64
import asyncio
from typing import Optional, Dict, Any

try:
    import numpy as np
except ImportError:
    np = None

from src.services.scanner import SCANNER_AVAILABLE
# Conditional import for cv2
try:
    import cv2
except ImportError:
    cv2 = None

if SCANNER_AVAILABLE:
    from src.services.scanner.pipeline import CardScanner
else:
    CardScanner = None

from src.services.ygo_api import ygo_service
from src.services.image_manager import image_manager
from nicegui import run

logger = logging.getLogger(__name__)

class ScannerManager:
    def __init__(self):
        self.running = False
        self.camera_index = 0
        self.scanner = CardScanner() if SCANNER_AVAILABLE else None

        # Queues
        self.frame_queue = queue.Queue(maxsize=1)
        self.lookup_queue = queue.Queue() # From CV Thread -> Main Loop
        self.result_queue = queue.Queue() # From Main Loop -> UI

        self.thread: Optional[threading.Thread] = None

        # State
        self.stable_frames = 0
        self.last_corners: Any = None
        self.is_processing = False
        self.cooldown = 0

        # Configuration
        self.stability_threshold = 10.0 # Max pixel movement allowed
        self.required_stable_frames = 5
        self.scan_cooldown_frames = 30 # Ignore same card for 30 frames after scan

    def start(self, camera_index: int = 0):
        if not SCANNER_AVAILABLE:
            logger.error("Scanner dependencies missing. Cannot start.")
            return

        if self.running:
            return

        self.camera_index = camera_index
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        logger.info(f"Scanner started on camera {camera_index}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        logger.info("Scanner stopped")

    def get_latest_frame(self) -> Optional[str]:
        """Returns the latest frame as a base64 string for UI display."""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        """Returns the latest scanned card data."""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

    def _worker(self):
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            if self.cooldown > 0:
                self.cooldown -= 1

            # Fast Detection
            contour = self.scanner.find_card_contour(frame)

            status_text = "Scanning..."
            color = (0, 255, 0)

            if contour is not None:
                # Check Stability
                if self._check_stability(contour):
                    self.stable_frames += 1
                else:
                    self.stable_frames = 0

                # Draw Contour
                cv2.drawContours(frame, [contour], -1, (0, 255, 255), 2)

                # Trigger Processing
                if self.stable_frames >= self.required_stable_frames and not self.is_processing and self.cooldown == 0:
                    self.is_processing = True
                    status_text = "Processing..."
                    color = (0, 0, 255)
                    # Run CV tasks in thread
                    threading.Thread(target=self._cv_scan_task, args=(frame.copy(), contour)).start()
                elif self.is_processing:
                    status_text = "Analyzing..."
                    color = (0, 0, 255)
                elif self.stable_frames > 0:
                    status_text = f"Stabilizing: {self.stable_frames}/{self.required_stable_frames}"
            else:
                self.stable_frames = 0
                self.last_corners = None

            # Overlay Status
            cv2.putText(frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            _, buffer = cv2.imencode('.jpg', frame)
            b64_str = base64.b64encode(buffer).decode('utf-8')

            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put(b64_str)

            time.sleep(0.01)

        cap.release()

    def _check_stability(self, contour) -> bool:
        """Checks if the contour corners have moved significantly."""
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) != 4:
            return False

        corners = approx.reshape(4, 2)
        corners = corners[np.argsort(corners.sum(axis=1))]

        if self.last_corners is None:
            self.last_corners = corners
            return False

        dist = np.max(np.linalg.norm(self.last_corners - corners, axis=1))
        self.last_corners = corners

        return dist < self.stability_threshold

    def _cv_scan_task(self, frame, contour):
        """Phase 1: Heavy CV extraction (Threaded)."""
        try:
            logger.info("Starting CV scan task...")
            warped = self.scanner.warp_card(frame, contour)

            # 1. OCR Set ID
            set_id = self.scanner.extract_set_id(warped)

            # 2. Detect Language (Visual/OCR)
            language = self.scanner.detect_language(warped, set_id)

            # 3. Detect 1st Edition
            first_ed = self.scanner.detect_first_edition(warped)

            # 4. Visual Rarity Fallback
            visual_rarity = self.scanner.detect_rarity_visual(warped)

            data = {
                "set_code": set_id,
                "language": language,
                "first_edition": first_ed,
                "rarity": "Unknown", # Will be resolved
                "visual_rarity": visual_rarity,
                "warped_image": warped # Pass warped image for Phase 2 (Art matching)
            }

            self.lookup_queue.put(data)

        except Exception as e:
            logger.error(f"Error in CV scan task: {e}")
            self.is_processing = False # Reset flag if error

    async def process_pending_lookups(self):
        """Phase 2: Data Lookup & Art Matching (Main Async Loop)."""
        try:
            try:
                data = self.lookup_queue.get_nowait()
            except queue.Empty:
                return

            logger.info(f"Processing lookup for Set ID: {data.get('set_code')}")

            set_id = data.get('set_code')
            warped = data.pop('warped_image', None) # Remove from dict to be clean

            # Default name
            data['name'] = "Unknown Card"
            data['card_id'] = None
            data['image_path'] = None

            if set_id:
                # 1. Resolve Card & Download Images
                card_info = await self._resolve_card_details(set_id)

                if card_info:
                    data.update(card_info)

                    # 2. Match Art (if multiple arts exist and we have the warped image)
                    if warped is not None and card_info.get("potential_art_paths"):
                        # Run ORB in thread to avoid blocking loop
                        match_path = await run.io_bound(
                            self.scanner.match_artwork, warped, card_info["potential_art_paths"]
                        )
                        if match_path:
                            data["image_path"] = match_path
                            logger.info(f"Art matched: {match_path}")
                        else:
                            data["image_path"] = card_info["potential_art_paths"][0]

            # Finalize Rarity
            if data["rarity"] == "Unknown":
                data["rarity"] = data["visual_rarity"]

            # Add to result queue
            self.result_queue.put(data)

            # Reset processing flag
            self.is_processing = False
            self.cooldown = self.scan_cooldown_frames

        except Exception as e:
            logger.error(f"Error in process_pending_lookups: {e}")
            self.is_processing = False

    async def _resolve_card_details(self, set_id: str) -> Optional[Dict[str, Any]]:
        """Finds card in DB and ensures images are downloaded."""
        # Clean ID
        set_id = set_id.upper()

        # 1. Search DB
        cards = await ygo_service.load_card_database("en")

        candidates = []
        for card in cards:
            if not card.card_sets: continue
            for s in card.card_sets:
                if s.set_code == set_id:
                    candidates.append((card, s))

        if not candidates:
            return None

        card, card_set = candidates[0]

        # 2. Download Images
        potential_paths = []
        if card.card_images:
            for img in card.card_images:
                path = await image_manager.ensure_image(card.id, img.image_url, high_res=True)
                if path:
                    potential_paths.append(path)

        return {
            "name": card.name,
            "card_id": card.id,
            "rarity": card_set.set_rarity,
            "potential_art_paths": potential_paths
        }

scanner_manager = ScannerManager()
