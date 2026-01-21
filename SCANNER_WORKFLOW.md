# Scanner Debug View: Detailed Workflow Explanation

This document explains the inner workings of the "Scan Debug View" functionality, covering the "Upload" and "Capture & Analyze" workflows, the backend processing logic, and the Computer Vision/OCR pipeline in detail.

## 1. System Architecture Overview

The scanning system operates on a decoupled architecture to prevent the User Interface (UI) from freezing during heavy image processing tasks.

*   **UI Layer (`src/ui/scan.py`)**: Built with NiceGUI/Quasar. It handles user input, renders camera feeds via JavaScript, and polls for status updates.
*   **Service Layer (`src/services/scanner/manager.py`)**: A singleton `ScannerManager` that runs a background worker thread. It manages a task queue, executes the pipeline, and holds the state.
*   **Pipeline Layer (`src/services/scanner/pipeline.py`)**: The `CardScanner` class containing the actual Computer Vision (OpenCV) and OCR (EasyOCR/PaddleOCR) logic.

---

## 2. Workflow A: Upload Picture
**Trigger**: User selects a file in the "Upload Image" component in the Debug Lab.

1.  **UI Event**: The `ui.upload` component triggers `handle_debug_upload(e)`.
2.  **File Read**: The system reads the binary content of the uploaded file (JPEG/PNG).
3.  **Submission**: The UI calls `scanner_manager.submit_scan(content, options, label="Image Upload")`.
    *   **Options**: Contains the active tracks (e.g., `['easyocr', 'paddle']`) and preprocessing mode (`'classic'` or `'yolo'`).
4.  **Queueing**: The manager wraps the image and options into a task dictionary (with a UUID and timestamp) and appends it to `self.scan_queue` (Thread-safe).
5.  **Feedback**: The UI immediately notifies "Queued: [Filename]" and refreshes the queue display.

---

## 3. Workflow B: Capture and Analyze
**Trigger**: User clicks the "Capture & Analyze" button in the Debug Lab.

1.  **UI Event**: The button triggers `handle_debug_capture()`.
2.  **JavaScript Bridge**: The Python backend sends a command to the browser: `await ui.run_javascript('captureSingleFrame()')`.
3.  **Client-Side Capture (JS)**:
    *   The browser script (`JS_CAMERA_CODE`) grabs the current frame from the active `<video>` element (id: `scanner-video` or `debug-video`).
    *   It draws the frame to a hidden canvas and converts it to a base64 Data URL (`data:image/jpeg;base64,...`).
4.  **Data Transmission**: The base64 string is returned to the Python backend.
5.  **Decoding**: `handle_debug_capture` decodes the base64 string back into raw bytes.
6.  **Submission**: The UI calls `scanner_manager.submit_scan(content, options, label="Camera Capture")`.
7.  **Queueing**: Similar to upload, the task is added to `self.scan_queue`.

---

## 4. The Backend Processing Loop
The `ScannerManager` runs a dedicated worker thread (`_worker`) that constantly monitors the queue.

1.  **Idle Check**: The loop checks if `scan_queue` is empty. If yes, it sleeps for **0.1s**.
2.  **Task Retrieval**: It pops the oldest task (FIFO) from the queue.
3.  **State Update**:
    *   `is_processing` becomes `True`.
    *   `status_message` updates to "Processing: [Filename]".
    *   The `debug_state` is initialized for this new scan.
4.  **Image Decoding**: The raw bytes are decoded into an OpenCV image (numpy array) using `cv2.imdecode`.
5.  **Debug Snapshot**: The raw input image is saved to disk (`debug/scans/manual_cap_....jpg`) and its URL is set in `debug_state['captured_image_url']` for the UI to show immediately.

---

## 5. The OCR Pipeline (`CardScanner`)
The manager calls `_process_scan`, which invokes methods in `src/services/scanner/pipeline.py`.

### Step 5.1: Preprocessing & Contour Detection (`find_card_contour`)
**Goal**: Locate the card within the image.

1.  **Grayscale & Blur**: Convert to grayscale and apply Gaussian Blur (5x5 kernel).
2.  **Morphological Gradient**: Computes the difference between dilation and erosion to highlight edges.
3.  **Otsu's Binarization**: Automatically calculates the optimal threshold to separate foreground (card) from background.
4.  **Contour Extraction**: Uses `cv2.findContours`.
5.  **Filtering**:
    *   **Area**: Discards contours smaller than **25,000 px**.
    *   **Scoring**: Calculates a "Central Bias" score. It penalizes contours far from the center (Distance weight: 0.5).
6.  **Geometric Verification**:
    *   Approximates the polygon (`epsilon = 0.02 * perimeter`).
    *   Calculates the bounding box (`cv2.minAreaRect`).
    *   **Aspect Ratio Check**: The width/height ratio must be between **0.55 and 0.85**.
    *   **Result**: The best fitting 4-point contour is returned.

### Step 5.2: Normalization (`warp_card`)
1.  **Perspective Transform**: The system takes the 4 points from the contour and maps them to a fixed standard size: **600x875 pixels**.
2.  **Result**: A flat, top-down view of the card (`warped_image`).
3.  **Debug**: This image is saved and displayed in the UI as "Perspective Warp".

### Step 5.3: ROI Visualization (`debug_draw_rois`)
The system draws colored rectangles on the warped image to show where it *will* look for text.
*   **Set ID (Red)**: `(300, 580, 290, 80)` - Bottom Right.
*   **Name (Cyan)**: `(30, 25, 480, 50)` - Top Left.
*   **1st Ed (Blue)**: `(20, 595, 180, 45)` - Bottom Left.
*   **Art (Magenta)**: `(50, 110, 500, 490)` - Center.

### Step 5.4: The Multi-Track OCR System
The system runs OCR up to 4 times per scan to maximize success rates.

*   **Track 1: EasyOCR**:
    *   **Full Frame**: Runs on the original uncropped image.
    *   **Cropped**: Runs on the 600x875 warped image.
    *   *Config*: `mag_ratio=1.5` (magnification) to detect small text.
*   **Track 2: PaddleOCR** (if enabled):
    *   **Full Frame**: Runs on the original image.
    *   **Cropped**: Runs on the warped image.
    *   *Config*: `cls=True` (angle classification).

### Step 5.5: Data Extraction (`_parse_set_id`)
For every OCR result, the system looks for the Set Code using Regex:
`([A-Z0-9]{3,4})[- ]?([A-Z]{0,2})?([0-9]{3})`
*   **Matches**: e.g., "LOB-EN001", "MRD-005".
*   **Confidence**: The raw OCR confidence is boosted by **+0.2** if the detected region is a known code (EN, DE, FR, etc.).
*   The result with the highest confidence score is selected.

---

## 6. Result & Feedback

1.  **Result Selection**: The `ScannerManager` compares the results from all 4 OCR passes (T1 Full, T1 Crop, T2 Full, T2 Crop) and picks the one with the highest confidence.
2.  **Database Lookup**:
    *   The system uses the detected **Set Code** (e.g., "LOB-EN001") to query the YGO Database.
    *   It retrieves the Card Name, Rarity, and Image URL.
3.  **UI Updates**:
    *   **Fast Loop (0.1s)**: The UI polls `scanner_manager.get_debug_snapshot()`. It updates the specific Debug Lab sections (Logs, captured image, warped image, individual OCR track results) in near real-time as the worker progresses.
    *   **Processing Loop (0.5s)**: Checks for the final "Scanned Card" result to add to the session list.

## Summary of Debug Lab Visuals
When you run a scan, you see:
1.  **Latest Capture**: The raw input (from upload or camera).
2.  **Perspective Warp**: The 600x875 crop (if contour detection succeeded).
3.  **Regions of Interest**: The warped image with colored boxes showing search zones.
4.  **OCR Results**: 4 collapsable panels showing exactly what text each engine found, allowing you to diagnose why a card might have been missed (e.g., glare on the Set ID region).
