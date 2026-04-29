# 🃏 OpenYuGi: The Ultimate Local-First Yu-Gi-Oh! Collection Manager

## 📖 TLDR: What is OpenYuGi?
OpenYuGi is an extremely comprehensive, local-first, privacy-focused collection manager and deck builder designed exclusively for Yu-Gi-Oh! collectors, competitive players, and developers. By leveraging plain-text JSON files instead of proprietary cloud databases, OpenYuGi guarantees that users retain full sovereignty over their inventory. The system offers extensive bulk-management tools, a professional deck builder with `.ydk` and banlist integration, complex multi-conditional filtering, physical storage location mapping, and an experimental hardware-accelerated AI webcam scanner.

Built with Python and the NiceGUI framework, OpenYuGi eliminates the need for user accounts, subscriptions, telemetry, and constant network synchronization. All data is written locally, enabling seamless third-party scripting, git-versioning of collections, and absolute data privacy. It is engineered from the ground up to support massive collections, utilizing lazy-loading, asynchronous input/output operations, and memory-efficient data structures to easily handle inventories exceeding tens of thousands of individual cards without frontend lag or database locking issues.

---

## ✨ Key Features and Advantages

### 🔹 High-Level Overview
OpenYuGi represents a fundamental shift from web-based inventory management to localized, developer-friendly data stewardship. At a high level, its most defining advantages include:

*   **Strict Local-First JSON Architecture:** Collections, decks, and metadata are persisted locally as heavily structured, type-safe Pydantic JSON schemas. There is no hidden SQL database; the text files *are* the database. This guarantees absolute data ownership and prevents vendor lock-in.
*   **Zero Cloud Reliance:** Images and database files are fetched via the external YGOPRODeck and Yugipedia APIs but are subsequently cached fully offline. The application can function indefinitely without an internet connection once the initial bootstrap is complete, ensuring your data is accessible even if external services go down.
*   **Robust State Management & Performance:** The NiceGUI frontend utilizes heavy lazy-loading and debounced I/O operations. It maintains a responsive UI thread by isolating all file operations to asynchronous background threads, preventing browser hanging or freezing during large batch updates.
*   **Extensive Cross-Referencing:** Every action (e.g., adding to a deck, assigning storage) recursively validates against a single source of truth for variant IDs and base IDs, ensuring data integrity across every module in the application. This eliminates issues with duplicate tracking of alternate card arts.
*   **Data Portability:** Because all collections and decks are standard JSON and YDK files, migrating to a new machine, creating backups, or sharing decklists is as simple as copying a directory. The entire state of your collection can be version-controlled using Git.
*   **Developer-Extensible:** Designed to be hacked on. Because the backend is pure Python, developers can easily write external scripts to parse their collection JSON, generate custom statistics, or interface with external tools without needing complex API keys or database connection strings.

### 🔹 Medium-Level Explanations by Module (Navigation & Pages)

#### 📦 Collection Management (The Core Hub)
The Collection tab serves as the primary gateway and the heart of OpenYuGi. Collections in OpenYuGi are distinct JSON files stored within the `data/collections/` directory. This architecture allows users to infinitely segment their inventory, cleanly isolating "Trade Binders" from "Main Binders", "Bulk Boxes", or even format-specific collections (e.g., "Goat Format Collection").

*   **Creating a Collection:** To initialize a new database, users navigate to the top-left dropdown within the Collection tab header, select the final option `+ New Collection`, provide a semantic name (like `My_Vintage_Collection`), and the system instantly provisions a new schema file on disk. You can create an unlimited number of these discrete collections.
*   **Adding Cards Manually:** Cards can be added directly via the intelligent Search Bar located in the header. The search dynamically filters the locally cached YGOPRODeck database. Clicking a search result opens the Detail View, prompting the user to define the exact specific Set Code (e.g., `LOB-EN001`), Rarity, Condition (NM, LP, MP, HP, DMG), Language (EN, DE, FR, etc.), and Edition (1st Ed, Unlimited) before committing the entry to the JSON file.
*   **View Modes (Consolidated vs. Collector):** The interface offers dual-state viewing to serve different user needs.
    *   **Consolidated View (Player Mode):** Aggressively aggregates all printings under the Base ID. This mode prioritizes gameplay metrics (e.g., showing a single tile for "Mystical Space Typhoon" and declaring "I own 15 copies across 6 sets"). This is essential when checking general availability for deck building.
    *   **Collectors View:** Flattens the hierarchy, rendering a distinct row for every unique combination of Set Code, Rarity, Condition, Language, and Edition. This prioritizes exact asset tracking for valuation or trading (e.g., "1x LOB 1st Ed NM", "3x SDY Unlimited LP").
*   **Complex Filtration:** The UI provides a powerful Filter Pane allowing for compound logic. Users can filter by strict Set Code (`| LOB`), specific Rarities (e.g., "Ultimate Rare"), ATK/DEF ranges, Pendulum Scales, Types, Attributes, and Ownership Boolean states (showing only cards you own, or showing all database cards). These filters dynamically update the view in real-time.

#### 📚 Browse Sets
A comprehensive database viewer utilizing locally cached API data. It visually maps entire booster sets, structure decks, and promotional releases.
*   **Visual Checklists:** Users can browse chronological releases and visually cross-reference their exact missing cards from specific legacy or modern releases.
*   **Master Set Tracking:** This is invaluable for users attempting to complete "Master Sets," as it provides a clear, visual indicator of exactly which specific rarities are missing from a given release.

#### 🗃️ Storage Assignment (Physical/Digital Bridge)
This module physically maps digital assets to real-world locations, solving the "I know I have this card, but where is it?" problem.
*   **Container Definition:** Users define distinct Storage Containers within the app (e.g., "Tin A", "Binder 2", "Slab Box", "Blue Deck Box").
*   **Assignment Mechanisms:** Within the Collection Detail View, Bulk Add interface, or Scanner Batch Commit, individual cards or stacks of cards can be explicitly assigned a specific `storage_location` string.
*   **Visual Management & Auditing:** The Storage tab visually renders these containers, displaying real-time volumetric capacities (e.g., "Binder 2 contains 350 cards"). It features an interactive, drag-and-drop enabled grid where users can utilize right-click context menus to mass-shift cards between physical bounds, ensuring the digital ledger perfectly mirrors reality after a physical reorganization.

#### 🛠 Professional Deck Builder
Engineered for competitive players who require exact precision, format legality checks, and deep integration with their physical inventory.
*   **.YDK Native Support:** The system natively parses and generates standard Yu-Gi-Oh! `.ydk` files. Files are saved directly to `data/decks/`, making them instantly and perpetually portable to competitive simulators like EDOPro, YGOOmega, and DuelingBook without requiring any proprietary format conversion or third-party websites.
*   **Banlist Context & Enforcement:** The Builder features real-time, dynamic enforcement of modern TCG, modern OCG, and historic formats (specifically Goat Format). As cards are added to the decklist, the engine cross-references the active banlist. Illegal cards exceeding copy limits (e.g., adding a 2nd Limited card) or forbidden statuses are aggressively highlighted with red borders within the visual interface.
*   **Deep Inventory Syncing (The Killer Feature):** Crucially, the Deck Builder deeply integrates with the user's active collections. It aggregates ownership via the internal `_resolve_card_id` mechanism. As you build a deck, a dynamic counter on each card tile displays exactly how many physical copies you own across all your collections and all alternate art variants. This instantly reveals if you need to purchase additional physical cardboard to legally sleeve the deck you are testing.
*   **Sub-Deck Routing:** The system intelligently routes cards to the Main Deck or Extra Deck based on their internal database typing (e.g., Synchro, Xyz, Link monsters are automatically partitioned), preventing illegal `.ydk` generation.

#### 🗄️ DB Editor (Local Data Override)
A local override system designed for absolute data sovereignty.
*   **Handling API Inaccuracies:** If external APIs contain errors regarding card levels, attributes, missing obscure set variants, incorrect text, or unreleased OCG promos, the DB Editor allows users to permanently mutate their local cache.
*   **Persistence:** These localized changes are prioritized and survive future database synchronizations. If the API says a card is a Spell but it is actually a Trap, your local override remains the ultimate source of truth, preventing the application from breaking due to external errors.

#### 🚀 Bulk Add & Import Tools
Designed for extremely high-throughput inventory loading, migrating users away from tedious manual single-card entry.
*   **Bulk Add Interface:** Features a localized, paginated view model. Users search a comprehensive library pane and utilize Drag-and-Drop operations to move entire stacks of cards into a staging area.
*   **Batch Operations:** Once cards are in the staging area, batch operation controllers can instantly apply specific Languages, Conditions, or Storage Locations to hundreds of cards simultaneously before committing the massive transaction to the database in a single atomic write.
*   **Import Migration:** The Import Tools permit parsing standard file types (like OpenYuGi JSON Backup files) to migrate massive collections effortlessly between instances or recover from backups, ensuring data is never trapped in an obsolete format.

#### 📸 AI Webcam Scanner (Beta)
A highly experimental, hardware-linked digitization tool aimed at eliminating manual data entry entirely. By employing OpenCV edge detection algorithms, Torch-based Machine Learning models for Optical Character Recognition (OCR), and a custom YOLO model (`yolo26n-cls.pt`), the system attempts to rapidly match physical cardboard to database entries via text parsing and visual art matching. (See the dedicated "Scanner Configuration & Requirements" section below for critical setup details).

---

## 🤖 LLM & AI Assistant Setup Guide

**ATTENTION LLM AGENTS (Codex, Claude, ChatGPT, Cursor, OpenDevin, Aider, etc.):**
If a user has provided this README to you, you must consider it your absolute foundational context for interacting with the OpenYuGi codebase. You are expected to synthesize this architecture completely before writing any code, running any bash commands, or modifying the application state. Read this section carefully; it contains the core operational constraints of this project. Deviation from these constraints will result in catastrophic failure of the application state.

### Core Architecture Constraints & Developer Directives

1.  **Strict Local-First / No Database Architecture:**
    *   There is absolutely NO SQL/NoSQL database (e.g., PostgreSQL, MySQL, SQLite, MongoDB) present in this application. Do not attempt to query one, install drivers for one, or suggest migrating to one.
    *   The term "Database" refers strictly and exclusively to atomic JSON file rewrites located in the `data/collections/` directory (for user data) and `data/db/` (for cached API metadata).
    *   The data state must be fully loaded into memory as Pydantic models. You do not issue queries; you load the JSON into a Python object, mutate the Python object, and atomically overwrite the JSON file using the provided persistence layer.

2.  **Pydantic Mutability & State Management:**
    *   Collections are rigorously parsed and validated using Pydantic schemas (defined in `src/core/models.py`).
    *   When implementing undo functionality, historical logging, or state duplication, you MUST use deep copying (e.g., `model.model_copy(deep=True)`) to prevent Python reference mutations from corrupting the active, live memory state before a file write occurs.

3.  **UI Framework Paradigms (NiceGUI):**
    *   The application is built entirely on the `NiceGUI` Python framework. You are interacting with a server-rendered, websocket-driven frontend. There is no React, Vue, or separate frontend repository.
    *   **Blocking I/O is Fatal:** Any file operations (JSON reading/writing), network requests, or heavy computational tasks (like image processing in the scanner) MUST be wrapped in `await run.io_bound(...)` or executed in separate background `asyncio` threads. Failing to do so will freeze the single-threaded `asyncio` event loop, dropping websocket connections and hanging the entire application UI for the user.
    *   **Responsive Design Layouts:** Avoid using fixed NiceGUI containers like `ui.grid(columns=X)` or `ui.row()` when designing responsive layouts. Instead, you must use standard HTML division blocks and apply Tailwind CSS directly: `ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4')`. This ensures mobile compatibility.
    *   **Lazy Loading is Mandatory:** When rendering UI elements containing massive datasets (e.g., `ui.select` dropdowns with thousands of card names), you must implement lazy-loading logic. Load a small initial subset and dynamically update the `options` property via search events, or the DOM will crash.

4.  **The Cardinal Rule of Card IDs (`_resolve_card_id`):**
    *   Yu-Gi-Oh! API data splits alternate arts and specific printings into entirely separate integer IDs.
    *   Any mathematical calculation regarding ownership, missing card counts, deck verification, or banlist enforcement MUST utilize the `_resolve_card_id` utility function.
    *   This function maps variant IDs back to the absolute Base ID. Failure to use this will result in the application failing to recognize that a user owns an alternate art of a card required for a deck, leading to false "missing card" warnings.

5.  **Testing Environment Restrictions & Mocking:**
    *   The isolated sandbox testing environment lacks network access and many deep dependencies.
    *   When executing `pytest` or writing verification scripts, you must heavily mock external modules (`nicegui`, `yaml`, `pydantic`, `requests`) *before* importing any source code to prevent catastrophic `ImportError` or `ModuleNotFoundError` exceptions.
    *   Specifically, mock `nicegui.ui.run_javascript` as an `AsyncMock`. The UI relies heavily on JS for specific DOM manipulations, and executing tests without mocking this will cause immediate execution failures.

---

## ⚙️ Installation & Execution Guide

This section details the explicit, step-by-step process required to bootstrap the OpenYuGi environment. It is written to be deterministic and robust enough for either a human developer or an automated AI agent to execute flawlessly across operating systems (Windows, macOS, Linux).

### System Prerequisites
Ensure the target machine meets the following baseline requirements before attempting installation:
*   **Python 3.10 or newer**: This is a strict requirement due to heavy reliance on modern `typing` paradigms (like the `|` union operator) and advanced `asyncio` features utilized by the underlying FastAPI and NiceGUI architecture. Verify with `python --version`.
*   **Git**: Required to clone the repository and manage version control.
*   **Sufficient Disk Space:** While the JSON data is small, downloading the full high-resolution image cache for all cards requires several gigabytes of storage.

### Step-by-Step Installation Procedure

1.  **Clone the Repository**
    Begin by pulling the source code to your local machine. Open a terminal or command prompt.
    ```bash
    git clone https://github.com/yourusername/openyugi.git
    cd openyugi
    ```

2.  **Initialize Virtual Environment (Required)**
    Create an isolated Python environment to house the project's dependencies safely. This prevents conflicts with system-level Python packages. Note: use `python -m virtualenv venv` or similar if the command below fails.

    *For Conda Environments (Recommended for robust cross-platform execution):*
    ```bash
    conda create -n openyugi python=3.10 -y
    conda activate openyugi
    ```

    *Alternatively, for standard Python virtualenv (Linux/macOS):*
    ```bash
    python3.10 -m virtualenv venv
    source venv/bin/activate
    ```

    *Alternatively, for standard Python virtualenv (Windows Command Prompt):*
    ```cmd
    python -m virtualenv venv
    .\venv\Scripts\activate
    ```

3.  **Install Python Dependencies**
    Execute the pip installation targeting the requirements file. This will pull NiceGUI, Pydantic, FastAPI, and all necessary structural libraries.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Scanner System Dependencies (Crucial for Hardware Access)**
    The experimental AI Scanner subsystem relies heavily on the OpenCV library and Tesseract OCR engine. These often require system-level C++ binaries to function correctly and cannot be installed via `pip` alone.

    *For Ubuntu / Debian Linux:*
    ```bash
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr libgl1-mesa-glx libglib2.0-0
    ```

    *For macOS (via Homebrew):*
    ```bash
    brew install tesseract
    ```

    *For Windows:*
    Download the Tesseract Windows Installer from the official UB-Mannheim GitHub repository. Execute the installer. **Critical Step:** You must explicitly check the box to "Add to PATH" during the installation process, or the Python `pytesseract` wrapper will fail to locate the executable, and the scanner will instantly crash.

5.  **Launch the Application Server**
    OpenYuGi operates via a localized Python server, utilizing uvicorn under the hood to serve the frontend. Ensure you are in the root directory of the repository.
    ```bash
    python main.py
    ```
    Upon successful initialization, the console will confirm the server is running, and the application will automatically bind to and be accessible via your default web browser at `http://localhost:8080`.

---

## 📚 Documentation Reference Index

For detailed architectural breakdowns, deep operational tutorials, and troubleshooting matrices, please consult the extensive technical guides located within the local `docs/` folder. These files provide granular insight into specific subsystems and should be read by both users and contributing developers:

*   **`docs/Home.md`**: The master index and general overview of the documentation repository. Start here.
*   **`docs/Collection.md`**: Granular breakdown of the complex data structures governing the consolidated vs. collector view state logic, and how JSON serialization is handled.
*   **`docs/DeckBuilder.md`**: A deep dive into the `.ydk` parser, the hierarchical banlist state enforcement algorithms, and the cross-reference logic used to determine ownership.
*   **`docs/Storage.md`**: Detailed explanation of the JSON storage schema, node assignment mapping, and the physical visualization logic governing the UI grids.
*   **`docs/CardScanning.md`**: Comprehensive pipeline documentation detailing the computer vision subsystem, OpenCV matrix transformations, OCR confidence scoring, and the machine learning models.
*   **`docs/BrowseSets.md` / `docs/BulkAdd.md` / `docs/DBEditor.md`**: Dedicated UI operational guides covering specific interaction flows and user expectations for those tabs.
*   **`docs/FAQ_Troubleshooting.md`**: Resolution strategies for common environment issues, hardware camera mapping failures, and database sync errors.

---

## 📸 AI Scanner Configuration & Details

The AI Scanner is OpenYuGi's most ambitious, complex, and experimental feature. It attempts to automate the digitization of physical cards using a multi-stage pipeline consisting of OpenCV Warp Perspective Correction, Optical Character Recognition (OCR), and Machine Learning Image Classification via YOLO.

Due to the highly unpredictable nature of physical cardboard—specifically the intense, light-scattering glare produced by Secret Rare, Ultimate Rare, and Quarter Century Secret Rare foil patterns—the scanner has exceedingly strict environmental and operational requirements. If these requirements are not met, the error rate will be unacceptably high.

### Critical Environmental Requirements
For the computer vision algorithms to achieve acceptable accuracy and confidence thresholds, the physical scanning setup MUST adhere to the following constraints:

1.  **Lighting Environment (The Most Important Factor):** The lighting must be heavily diffused, even, and entirely indirect. Direct overhead lighting, ring lights pointing directly down at the card, or flash photography will cause catastrophic glare on foil patterns. This glare completely blinds the OCR engines (turning text into white noise) and thoroughly confuses the YOLO feature matching models. Bouncing a desk lamp off a wall or using heavily frosted diffusers is required.
2.  **Background Surface:** The card MUST be placed on a dark, solid, non-reflective background (e.g., a clean black cloth playmat or dark matte cardstock). The initial stage of the pipeline relies on standard OpenCV edge-detection algorithms to find the four corners of the card. These algorithms require stark, immediate contrast between the physical card border and the background surface to accurately calculate the matrix required to digitally flatten (warp) the card image before OCR processing.
3.  **Hardware Mount:** A 1080p minimum webcam must be mounted stably and completely parallel to the scanning surface to minimize extreme geometric angles that distort text aspect ratios.

### Debug Lab Options & Processing Tracks
The "Debug Lab" tab within the Scanner UI provides advanced users with critical tuning parameters and visual feedback on the pipeline's execution. Understanding these toggles is essential for optimizing the scanner for specific hardware setups or specific eras of cards.

*   **Preprocessing Modes:** Dictates how the raw video frame is manipulated before edge detection.
    *   *Classic:* Standard thresholding, grayscale conversion, and Canny edge detection. Best utilized for highly controlled, high-contrast setups. It is extremely fast computationally.
    *   *YOLO / YOLO26:* Bypasses traditional OpenCV edge detection and leverages the local `.pt` machine learning models to isolate the card bounding box regardless of contrast or background noise. It is slower computationally but significantly more robust against messy desks, patterned playmats, or complex backgrounds.
*   **Active OCR Track:** Determines which engine attempts to read the card's Set Code.
    *   *EasyOCR:* A faster, lighter weight engine. While quick, it often struggles heavily with the highly stylized, tightly kerned, and sometimes compressed fonts utilized on Yu-Gi-Oh! cards, especially on highly reflective older printings.
    *   *DocTR:* Slower and carries a much heavier Torch processing dependency, but provides vastly superior accuracy on complex text layouts, skewed angles, and microscopic set code parsing. Highly recommended for modern hardware with GPU acceleration.
*   **Art Style Match (YOLO):** Toggles the secondary identification pass. If the OCR successfully extracts the Set Code (e.g., `LOB-001`), but multiple rarities exist for that code (e.g., an Ultra Rare and a 25th Anniversary reprint), the system passes the cropped card art to a custom YOLO model. This model attempts to determine the exact specific printing based on visual foil patterns, set stamps, and holo-markers.
*   **Ambiguity Threshold:** A slider determining the confidence delta required before the scanner interrupts the automated batch flow. If the engine is unsure (e.g., distinguishing between an Unlimited and 1st Edition variant where the gold stamp is slightly obscured by glare), it will halt and prompt the user via the Ambiguity Dialog to manually select the correct printing. Lowering this increases scanning speed but raises the error rate; raising it ensures accuracy at the cost of requiring manual intervention.

---

## 📋 Comprehensive List of Features

Below is the exhaustive, technical enumeration of all features currently supported by the OpenYuGi platform.

**Core Architecture & Engine**
*   Completely local data persistence utilizing isolated, version-controllable JSON schemas.
*   Fully decoupled UI and Business Logic layer via the Python NiceGUI framework, enabling headless operation if desired.
*   Purely offline-first operation capability following the initial database bootstrap synchronization.
*   Asynchronous file I/O operations guaranteeing a non-blocking, fluid user interface even under massive data loads (100,000+ card entries).
*   Image lazy-loading and dynamic caching system to drastically reduce memory footprint and network bandwidth during heavy browsing sessions.

**Advanced Inventory Control**
*   Support for practically unlimited collection sizes spanning multiple segmented, user-defined JSON files.
*   Dual-state interface viewing:
    *   Consolidated (Player) Mode for rapid gameplay metric assessment and deck availability.
    *   Collector (Variant) Mode for granular asset tracking, valuation, and specific printing identification.
*   Hyper-granular property tracking capturing exact Condition states (NM, LP, MP, HP, DMG), specific Language localizations (EN, DE, FR, IT, ES, PT, JP, KR), and Edition classifications (1st Edition, Unlimited, Limited).
*   Deep Undo/Redo service tracking database mutations via atomic snapshots, allowing instantaneous reversion of accidental modifications or large batch errors.

**Filtration, Sorting & Querying**
*   Compound filtering logic supporting intersecting queries across Card Name, exact Set Code parsing, Attribute, Level, Pendulum Scale, and specific ATK/DEF integer parameters.
*   Advanced internal archetype resolution mapping and detailed Monster Category filtering (e.g., separating Tuners, Spirits, Unions, Gemini, Toons).
*   Real-time dynamic UI sorting algorithms allowing instant reorganization by Set Code chronology, Rarity hierarchy, numerical quantities, or alphabetical indexing.

**Professional Deck Engineering**
*   Multi-format Banlist enforcement engine, actively pulling and applying validation logic for modern TCG, modern OCG, and curated historic formats like Goat Format or Edison Format.
*   Native, direct `.ydk` Import/Export architecture ensuring absolute compatibility with the wider competitive simulator ecosystem (EDOPro, YGOOmega).
*   Bi-directional inventory synchronization reflecting active, real-time physical ownership counts against theoretical decklists, factoring in all alternate arts via `_resolve_card_id`.
*   Intelligent sub-deck routing ensuring correct placement of Extra Deck and Main Deck entities based on internal card typing, preventing formatting errors.
*   Genesys / Custom Point format tracking (if configured).

**Physical Storage Mapping**
*   Virtual to physical correlation logic using user-defined hierarchical Storage Location nodes (Binders, Boxes, Tins).
*   Interactive, visual grid management system displaying real-time container capacities and occupancy rates across all defined locations.
*   Batch contextual migration allowing massive block moves of digital cards across defined physical bounds in a single click.

**Ingestion & Data Migration Tools**
*   High-throughput, dual-pane Drag-and-Drop Bulk Add interface optimized for rapid sequence entry of large purchases or bulk boxes.
*   Mass batch-update controllers to simultaneously apply uniform Condition, Language, or Storage assignments to hundreds of staging entries prior to database commit.
*   Robust JSON Schema Backup and Restoration architecture enabling foolproof system migrations and disaster recovery.

**Experimental Hardware & ML Integrations (Scanner)**
*   Local GPU/CPU accelerated multi-track OCR pipeline utilizing DocTR or EasyOCR integrations for text parsing.
*   Custom-trained YOLO variant (`yolo26n-cls.pt`) implementation specifically designed for Yu-Gi-Oh! card boundary isolation and highly specific art/foil pattern recognition.
*   Automated batch-commit queue supporting high-speed continuous scanning sessions without requiring intermediate user input for clean reads.
*   Real-time visual Debug Lab exposing matrix transformations, region of interest (ROI) extraction paths, and algorithmic confidence scoring to the user.
*   Ambiguity resolution dialog forcing user intervention when hardware confidence drops below user-defined thresholds.

---

## 🛠 Advanced Developer Topics

This section provides deeper insight into the technical decisions and design patterns used within OpenYuGi, intended for developers looking to contribute or write external tooling against the data schemas.

### The Storage JSON Schema (`data/collections/`)

The fundamental premise of OpenYuGi is that your data should be human-readable and instantly parseable. To this end, every collection is a discrete JSON file structured under a rigid Pydantic model (`src.core.models.Collection`).

A typical collection file looks like this structurally:

```json
{
  "name": "Main_Binder",
  "storage_definitions": [
    { "id": "uuid-1", "name": "Binder 1" },
    { "id": "uuid-2", "name": "Bulk Box" }
  ],
  "cards": [
    {
      "card_id": 46986414,
      "name": "Dark Magician",
      "variants": [
        {
          "variant_id": "LOB-EN005_Ultra Rare",
          "set_code": "LOB-EN005",
          "rarity": "Ultra Rare",
          "image_id": 46986414,
          "entries": [
            {
              "quantity": 2,
              "condition": "Near Mint",
              "language": "EN",
              "first_edition": true,
              "storage_location": "Binder 1",
              "purchase_price": 0.0,
              "purchase_date": "2024-01-01T12:00:00"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Hierarchical Depth Explanation:
1.  **`cards` (List):** The top-level array groups everything by the `card_id` (The YGOPRODeck base passcode). This grouping is what makes the "Consolidated Player View" so fast; it doesn't have to search the entire database to find all Dark Magicians, it just grabs this node.
2.  **`variants` (List):** Inside a card, it breaks down into specific printings. A variant is uniquely defined by the combination of its `set_code` and `rarity`. This resolves issues where a set contains both an Ultra Rare and an Ultimate Rare version of the same card with the same set code.
3.  **`entries` (List):** Inside a variant, the actual physical instances are recorded. An entry is a unique combination of `condition`, `language`, and `first_edition` flags. If you have two Near Mint English 1st Editions, they are grouped in one entry with `quantity: 2`. If you have one Near Mint and one Lightly Played, they exist as two separate entries.

### The API Cache Layer (`data/db/`)

To achieve true offline-first capability, OpenYuGi does not ping YGOPRODeck every time a search is performed. Instead, it downloads the entire metadata library during the initial setup and stores it locally.

*   `ygo_card_db_{lang}.json`: Contains the parsed, minified representation of every card in the game (Stats, Text, Attributes).
*   `ygo_set_db_{lang}.json`: Contains the structural mapping of every release (Booster Packs, Structure Decks) and the specific cards/rarities contained within them.

**Developer Note:** If you are writing scripts to analyze value or missing cards, do NOT ping the external API. Load these local JSON files into memory. They are significantly faster and prevent rate-limiting.

### Asynchronous Event Loop Management (NiceGUI)

OpenYuGi utilizes NiceGUI, which sits on top of FastAPI and Uvicorn. This means the entire backend is running in a single `asyncio` event loop.

If you introduce synchronous, blocking code (like `time.sleep()`, heavy `pandas` dataframe processing, or complex file I/O) directly into a UI event handler (like an `on_click` event), the entire application will freeze for all connected clients. The websocket heartbeat will drop, and the UI will lock up.

**Always use `run.io_bound` for blocking tasks:**

```python
# BAD: Will freeze the UI thread
def on_button_click():
    with open('massive_file.json', 'r') as f:
        data = json.load(f)

# GOOD: Offloads to a separate background thread
async def on_button_click():
    data = await run.io_bound(load_massive_file, 'massive_file.json')
```

### The Scanner Image Pipeline (Detailed)

If you are modifying the `src/services/scanner/` modules, you must understand the sequential flow of the pipeline. It is not a single black box, but a series of distinct, measurable steps.

1.  **Capture (`captureSingleFrame`):** A raw base64 frame is grabbed from the HTML5 `<video>` element.
2.  **Preprocessing (`OpenCV`):** The image is converted to grayscale, Gaussian blurred, and subjected to adaptive thresholding.
3.  **Edge Detection (`cv2.Canny` / `findContours`):** The system attempts to find the largest four-point polygon in the frame.
4.  **Perspective Warp (`cv2.getPerspectiveTransform`):** Once the corners are found, the skewed polygon is mathematically flattened into a perfect rectangle, normalizing the aspect ratio of the text.
5.  **ROI Extraction (Region of Interest):** Because the set code and name are always in the same relative position on a Yu-Gi-Oh! card, the system crops out just the specific horizontal strips containing the Name, Set Code, and Edition text.
6.  **OCR Pass (`DocTR` or `EasyOCR`):** The cropped ROIs are passed to the deep learning models to extract raw strings.
7.  **Fuzzy Matching (`FuzzyWuzzy` / Levenshtein):** The raw strings are checked against the local database to find the closest legal Set Code and Card Name.
8.  **Art Matching (`YOLO` - Optional):** If the Set Code is ambiguous regarding rarity, the center art box is cropped and passed to the YOLO model to identify specific foil reflection patterns.

When debugging scanner failures, always check the "Debug Lab" output to see exactly which step failed (e.g., did it fail to find the corners, or did it find the corners but fail to read the warped text?).

---

## 🤝 Contributing & Pull Requests

OpenYuGi is an active, open-source project, and contributions are heavily encouraged. Whether you are fixing typos in the documentation, optimizing the OpenCV algorithms, or adding support for new API data sources.

**Pull Request Workflow:**
1.  Fork the repository to your own GitHub account.
2.  Create a feature branch off of `main` (e.g., `git checkout -b feature/improved-yolo-model`).
3.  Implement your changes. Ensure you adhere to the asynchronous NiceGUI constraints detailed above.
4.  Run the verification scripts located in the `/verification` folder (if applicable) to ensure you haven't broken core UI elements.
5.  Submit a Pull Request detailing the changes, the problem it solves, and any new dependencies introduced.

*Built with ❤️ by the OpenYuGi Community. Your data, your drive.*

---

## 🏗 Subsystem Deep Dives

To ensure absolute clarity on the depth of the application, here are exhaustive breakdowns of secondary subsystems that power the overarching features.

### 🔄 The Undo / Redo Logging Architecture

One of the most complex features of a local-first application is providing robust, transaction-safe undo capabilities without a SQL transaction log. OpenYuGi solves this via a custom `UndoService` and `ChangelogManager`.

*   **Atomic Transactions:** Every action that mutates the collection state (adding a card, deleting a card, batch updating conditions) is treated as a discrete transaction.
*   **Deep State Snapshots:** Before the mutation is committed to disk via `persistence.save_collection()`, the system captures a deep copy of the relevant objects. It logs the exact parameters of the change (e.g., `ACTION: ADD`, `QUANTITY: 3`, `VARIANT: LOB-001`, `TARGET_LOCATION: Binder A`).
*   **The Inversion Engine:** When a user clicks the "Undo" button, the `UndoService` reads the last log entry from the respective collection's changelog file. It then calculates the exact inverse mathematical operation. If the action was `ADD 3`, the inverse is `REMOVE 3`.
*   **Batch Rollbacks:** For massive operations (like moving 500 cards from "Binder 1" to "Bulk Box"), the system doesn't log 500 individual actions. It logs a single `BATCH_UPDATE` transaction. A rollback instantly reverts all 500 cards to their previous state in a single, atomic file write, preventing partial state corruption.

### 🎨 The UI Component Architecture (Tailwind + Vue via NiceGUI)

While developers write pure Python, it is crucial to understand what the framework is actually compiling down to. NiceGUI acts as a bridge, converting Python object instantiations into Vue.js components, styled heavily with Tailwind CSS utility classes.

*   **The `classes()` Method:** This is the primary mechanism for styling. Instead of writing external CSS files, OpenYuGi heavily relies on Tailwind strings. For example: `ui.card().classes('w-full bg-gray-900 border border-gray-700 shadow-xl')`.
*   **Flexbox and Grid Paradigms:** The application relies entirely on modern flexbox (`flex`, `items-center`, `justify-between`) and CSS grid (`grid`, `grid-cols-12`, `gap-4`) for its layout structure. Developers modifying UI components must be fluent in standard Tailwind layout paradigms.
*   **The `props()` Method:** This allows passing direct Vue component properties to the underlying Quasar framework elements (which NiceGUI wraps). For example, `ui.button('Save').props('unelevated color="primary" icon="save"')`.
*   **Websocket Hydration:** When a backend Python variable changes, NiceGUI sends a tiny JSON payload over the active websocket to the browser, telling Vue to re-render only the specific DOM node bound to that variable. This is why heavy computational blocking on the backend causes the UI to freeze; the websocket heartbeat is interrupted, and the DOM cannot update.

### 🌍 Language Localization & Region Compatibility

The Yu-Gi-Oh! ecosystem is notoriously fractured across regions (TCG vs. OCG), languages, and specific regional printings (e.g., European English vs. North American English). OpenYuGi attempts to map this chaos deterministically.

*   **The `is_set_code_compatible` Algorithm:** Located in `src/core/utils.py`, this function is the bedrock of language filtering. It analyzes the specific set code (e.g., `LOB-EN001` vs. `LOB-E001` vs. `LOB-G001`).
*   **Regional Prefixes:** It understands that `EN` dictates an English printing, `G` or `DE` dictates German, `F` or `FR` dictates French, and `J` or `JP` dictates Japanese (OCG).
*   **Strict Filtering:** When a user filters a collection view by "Language: German", the system doesn't just look at a generic language tag. It validates that the underlying set code physically matches known German regional prefixes, preventing impossible combinations (like a Japanese Set Code flagged as English).

### 📈 ECharts Integration for Data Visualization

OpenYuGi utilizes the Apache ECharts library (via NiceGUI's `ui.echart` integration) to provide professional-grade, interactive data visualization, particularly within the Dashboard and Storage modules.

*   **Dynamic JSON Configuration:** ECharts are driven entirely by complex JSON configuration dictionaries built dynamically in Python.
*   **Responsive Canvas Rendering:** Because ECharts render via HTML Canvas, they require explicit height and width definitions to render correctly, especially within dynamic flex containers. Developers must ensure classes like `w-full h-full min-h-[300px]` are applied to chart containers, otherwise the canvas will collapse to 0px height on mobile viewports.
*   **Event Binding:** The charts are not static images. The Python backend binds to JavaScript click events on the canvas. Clicking a specific pie slice in the "Rarity Breakdown" chart can dynamically trigger a UI state change, filtering the main collection view to only show cards matching that rarity.

### 🛡 Security & Privacy Posture

Because OpenYuGi is a local-first application, its security model is fundamentally different from a SaaS platform.

*   **No Authentication Vectors:** There are no usernames, passwords, API tokens (for user data), or OAuth flows. The security of the data is directly tied to the security of the host operating system's file system.
*   **Network Isolation:** Aside from fetching public API metadata (images and card text) from YGOPRODeck, the application makes zero external network calls. It never phones home, it reports no telemetry, and it cannot sync data to the cloud without the user explicitly writing a third-party synchronization script (e.g., using a cron job with `rclone` or Dropbox).
*   **Sanitization:** While there is no database to suffer SQL injection, the system heavily sanitizes inputs when parsing `.ydk` files or importing external CSVs to prevent arbitrary code execution or path traversal vulnerabilities during file saving operations.

---

## 🔮 The Future Roadmap

OpenYuGi is in active development. The architectural foundation is solid, but the feature set is continually expanding. The immediate roadmap includes:

1.  **Mobile Interface Optimization:** While Tailwind provides baseline responsiveness, the application requires dedicated mobile views for complex grids (like the Deck Builder) to be truly usable on a 6-inch touchscreen.
3.  **CUDA Acceleration for Scanner:** Currently, the scanner runs heavily on CPU operations via OpenCV and Torch CPU. Transitioning the matrix calculations and Torch inferences to leverage native CUDA cores will dramatically increase scanning FPS and reduce frame latency.
4.  **Custom Banlist Creation UI:** Allowing local tournament organizers to visually construct custom banlists (e.g., "Heartland Format") and enforce them locally within the Deck Builder, saving them as distributable JSON files.
5.  **Automated Dependency Management Scripts:** Streamlining the OpenCV/Tesseract installation process on Windows/Linux via a single execution script, eliminating the need for manual system path configuration.

---

## 📜 Licensing and Legal

**OpenYuGi** is released under the **MIT License**.

This project is a fan-made, open-source tool. It is completely independent and is not affiliated with, endorsed, sponsored, or specifically approved by Studio Dice, Shueisha, TV Tokyo, Konami, or any of their affiliates.

Yu-Gi-Oh! is a trademark of Studio Dice/Shueisha, TV Tokyo, Konami. All card images, card text, and related indicia are copyrighted materials belonging to their respective creators and publishers. OpenYuGi utilizes external, public APIs (such as YGOPRODeck) solely for the purpose of retrieving publicly available metadata to facilitate personal, non-commercial collection management. The software itself acts only as a local data processor and visualization tool for user-generated text files.

---

## 🧰 Developer Bootstrapping & Scripting Examples

Because OpenYuGi utilizes flat JSON files, it is incredibly easy for users to write their own custom Python scripts to interact with their collection data without ever booting up the NiceGUI interface. This is the true power of data sovereignty.

### Example 1: Basic Collection Parsing
This script demonstrates how to load a collection and print out a simple text-based inventory, showcasing the hierarchical structure of the data.

```python
import json

def print_inventory(collection_path):
    # Load the JSON file directly
    with open(collection_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"--- Inventory: {data.get('name', 'Unknown')} ---")

    total_cards = 0

    # Iterate through the top-level cards (Base IDs)
    for card in data.get('cards', []):
        card_name = card.get('name', 'Unknown Card')

        # Iterate through the specific set printings
        for variant in card.get('variants', []):
            set_code = variant.get('set_code', '???')
            rarity = variant.get('rarity', '???')

            # Iterate through the physical instances
            for entry in variant.get('entries', []):
                qty = entry.get('quantity', 0)
                condition = entry.get('condition', 'Unknown')
                lang = entry.get('language', 'EN')
                first_ed = "1st Ed" if entry.get('first_edition') else "Unlim"
                location = entry.get('storage_location', 'Unassigned')

                print(f"{qty}x {card_name} [{set_code}] - {rarity}")
                print(f"    -> {condition} | {lang} | {first_ed} | Loc: {location}")

                total_cards += qty

    print(f"--- Total Physical Cards: {total_cards} ---")

# Execute the function against the default collection
print_inventory('data/collections/collection.json')
```

### Example 2: External Backup Automation (Linux/macOS)
You don't need complex cloud sync plugins. Because the data is just text, standard OS tools work perfectly. This is an example of a simple bash script that could be run via a daily cron job to backup the entire application state.

```bash
#!/bin/bash
# backup_openyugi.sh

# Define paths
SOURCE_DIR="/path/to/openyugi/data"
BACKUP_DIR="/path/to/dropbox/OpenYuGi_Backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
ARCHIVE_NAME="openyugi_backup_$DATE.tar.gz"

echo "Starting OpenYuGi Backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Archive the data directory (excluding the massive image cache)
tar -czvf "$BACKUP_DIR/$ARCHIVE_NAME" \
    --exclude="$SOURCE_DIR/images" \
    --exclude="$SOURCE_DIR/scans/raw_images" \
    "$SOURCE_DIR"

echo "Backup complete: $BACKUP_DIR/$ARCHIVE_NAME"

# Optional: Delete backups older than 30 days to save space
find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +30 -exec rm {} \;
echo "Cleaned up old backups."
```

### Example 3: Modifying the API Database (Advanced)
If you are a developer and want to interact with the core Pydantic models directly (simulating what the UI does), you can import the internal services directly. You must run this script from the root of the repository to ensure relative imports resolve correctly.

```python
import asyncio
from src.core.persistence import persistence
from src.services.ygo_api import ygo_service
from src.core.models import ApiCard

async def custom_db_override():
    print("Loading Global API Cache...")
    # Initialize the service, this loads the massive JSON caches into memory
    await ygo_service.initialize()

    target_id = 46986414  # Dark Magician

    # Retrieve the Pydantic model
    card = ygo_service.get_card(target_id)
    if not card:
        print("Card not found!")
        return

    print(f"Original Name: {card.name}")
    print(f"Original Type: {card.type}")

    # Mutate the model directly
    card.name = "Dark Magician (Custom Override)"
    card.type = "Normal Spell Card" # A nonsensical override for demonstration

    # The DB Editor service handles saving this back to the JSON file safely
    from src.services.db_editor import db_editor

    # Persist the change
    db_editor.save_card_override(target_id, card.model_dump())
    print("Override saved successfully to local database.")

# Run the async script
if __name__ == "__main__":
    asyncio.run(custom_db_override())
```

These scripts highlight the philosophy of OpenYuGi: The application is just a powerful UI wrapped around standard, accessible, and easily manipulable text files. Your data is always ready for whatever workflow you need.
