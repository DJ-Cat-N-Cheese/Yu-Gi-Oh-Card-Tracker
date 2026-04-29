# 🃏 OpenYuGi

> **The Ultimate Local-First Yugioh Collection Manager**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![NiceGUI](https://img.shields.io/badge/Built_with-NiceGUI-red.svg)](https://nicegui.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active_Development-green)](https://github.com/yourusername/openyugi)

---

## 🤖 LLM Setup & Installation Guide (Read First)

**OpenYuGi is designed to be easily configurable by AI.**
If you are setting this up, simply copy and paste the *entire text of this README* into an LLM (like Claude, ChatGPT, or GitHub Copilot/Codex) and ask it:
> *"I want to set up OpenYuGi on [Windows/Mac/Linux]. Please guide me step-by-step through installing the dependencies, including the complex scanner tools (like Tesseract and Torch) and starting the server."*

The LLM will extract everything it needs from the comprehensive architecture details and setup instructions below to generate a tailored script specifically for your operating system and environment. Because OpenYuGi relies heavily on local hardware integration for its AI scanner—requiring complex binaries like Tesseract and specific OpenCV library configurations—an LLM can save you significant time by generating platform-specific environment variables and package manager commands. By passing this entire document, the LLM will also understand the exact data structures (JSON files, Pydantic validation) allowing you to ask it to write custom export scripts or Python analysis tools instantly.

---

## 📖 TL;DR: What is OpenYuGi?

OpenYuGi provides a complete, uncompromising solution for managing physical Yu-Gi-Oh! collections without ever forcing you to upload your data to a server.

By operating entirely as a local web app on your machine, it guarantees absolute privacy and data ownership through transparent JSON files. Whether you are building tournament-legal `.ydk` decks, tracking thousands of specific foil variants across multiple physical binders, or mass-digitizing bulk piles with a high-speed webcam OCR scanner, OpenYuGi handles massive scale instantly. It is built for power users who demand speed, granular control over their data, and an ad-free, account-free experience.

Most cloud-based managers suffer from latency when filtering tens of thousands of cards. Because OpenYuGi loads your entire collection into memory directly from your hard drive, filtering, searching, and sorting happen in real-time, leveraging the full power of your CPU without waiting for network requests. There are absolutely zero required subscriptions, premium tiers, or required accounts.

---

## ✨ Key Features

### For The Serious Collector:
* **Absolute Privacy & Data Ownership:** Your collection is yours. Because everything is stored locally in human-readable JSON files, you are never locked out of your own inventory. If OpenYuGi ceases development tomorrow, your data is completely safe and accessible on your local drive. You can back it up to a thumb drive and keep it in a safe.
* **Infinite Granularity & Variant Tracking:** Most collection managers treat a "Blue-Eyes White Dragon" as a single entity. OpenYuGi allows you to track an infinite number of distinct variants. You can track exact set codes, 1st Edition vs Unlimited, specific languages, and specific physical conditions natively.
* **Collector vs. Player View Toggle:** OpenYuGi understands that players and collectors look at cards differently. The UI allows you to toggle instantly between viewing consolidated playsets (Player Mode - "I have 5 Mystical Space Typhoons across various sets") and distinct physical printings (Collector Mode - "I have two SDK-001 Commons and three MRL-047 Secret Rares").
* **Physical Storage Emulation:** Create unlimited custom "Binders" and "Boxes" within the application. You can assign individual cards to these digital storage containers, ensuring you always know exactly which physical box under your bed contains your specific tech cards.
* **Condition & Language Metatags:** Track exactly if your card is Near Mint, Lightly Played, Moderately Played, Heavily Played, or Damaged. Track language tags like English, German, French, Italian, Spanish, Portuguese, and Japanese natively with high-resolution visual flags in the UI.
* **Master Set Tracking Integration:** Built-in "Browse Sets" logic that allows you to click on any official Konami set (like Legend of Blue Eyes White Dragon or Pharaoh's Servant) and instantly see a visual grid of every card in that set, color-coded by whether you own it or are missing it. This makes tracking completion percentages for master sets effortless.

### For The Competitive Player:
* **Tournament-Ready Pro Deck Builder:** A comprehensive deck-building interface that rivals dedicated simulators. It dynamically validates your deck against current Advanced TCG, OCG, and historical formats like Goat Format or Edison Format.
* **Real-Time Physical Cross-Referencing:** As you build a deck, OpenYuGi actively checks your local JSON collection database. If you add three "Ash Blossom & Joyous Spring" to your list, the builder will visually indicate if you actually own three physical copies, or if you only own two and need to proxy/purchase a third.
* **YDK Interoperability:** Full support for standard `.ydk` files. You can export your decks straight from OpenYuGi to your favorite online simulators like EDOPro, YGOOmega, or Duelingbook without manual transcription. Conversely, you can drag and drop `.ydk` files you downloaded from tournament tops straight into the app.
* **No Telemetry, No Lag:** Because everything runs entirely locally on your own machine, filtering and searching through tens of thousands of cards is instantaneous. You never have to wait on a server to respond to a search query.
* **Advanced Extra Deck Logic:** Automatically sorts Link, Xyz, Synchro, and Fusion monsters directly into the Extra Deck during drag-and-drop operations so you never build an illegal deck state by accident.

### Navigating the App: How You Manage Your Collection
OpenYuGi provides a suite of specialized UI tabs to interface with your offline database, accessed via a responsive sidebar:

* **The Collection Tab:** The main viewing area for your inventory. It features a massive data grid optimized to lazy-load thousands of high-res images without crashing. You interact with a robust Filter Pane to execute complex queries (e.g., "Show me only Level 4 WATER monsters, that I own at least 3 copies of, from Labyrinth of Nightmare") and toggle between consolidated player views and granular collector views. The grid uses infinite scrolling to preserve DOM memory.
* **The Deck Builder Tab:** A professional visual sandbox for creating `.ydk` format decks. You drag and drop cards from a massive searchable library into your Main, Extra, and Side decks. The engine enforces live banlist checking (TCG/OCG/Goat), turning illegal cards red. Crucially, a dynamic counter on every card cross-references your JSON files, warning you instantly if you are slotting in copies you do not physically own. The UI provides visual breakdowns of monster/spell/trap ratios and deck size limits.
* **The Storage Tab:** A gallery-style interface representing your physical inventory. Here, you define virtual Binders and Boxes, assigning physical cards to them. You can click into a binder to view its contents and use a streamlined transfer interface to execute atomic move operations, ensuring digital location perfectly maps to physical reality. It also calculates the unique variants held within each specific binder.
* **The AI Scanner Tab:** The interface for the local computer-vision engine. It displays your live webcam feed with real-time bounding box overlays. As you scan cards, they populate a "Batch Queue", allowing you to review dozens of cards, apply bulk edits (like setting the entire batch to "Lightly Played"), and commit them to your database simultaneously. It includes a debug window to view the computer vision parameters.
* **Import & Export Tools:** The gateway for data migration. This tab allows you to export your entire database to CSV for spreadsheet analysis, create complete JSON backup snapshots, or import raw text strings and third-party stock files directly into actual database entries. It features regex parsing to handle complex unstructured string formats.
* **Bulk Add Tab:** Designed for entering massive decklists or purchased lots manually. It uses a split-pane drag-and-drop interface powered by SortableJS, allowing you to drag massive lists of cards from search results directly into your collection. The right pane serves as a temporary staging area before committing thousands of cards to the JSON database.
* **Browse Sets Tab:** The gateway for pure completionists. Click on any canonical Yu-Gi-Oh! booster pack or starter deck and see the entire set list in chronological order. The UI dynamically colors cards you own versus ones you are missing, calculating exactly what percentage of the master set you have completed, and highlighting the exact missing variants.
* **DB Editor Tab:** A low-level developer utility for power users. If the YGOPRODeck API is wrong, or if a brand new proxy set was just printed by the community, you can manually override card data, adjust attack and defense values, fix missing rarities, and insert custom Set Codes directly into the SQLite-like local cache without waiting for an official patch.

---

## 🚀 Installation & Setup Guide

Because OpenYuGi relies on local machine learning models for its scanner, setting up the environment requires a few specific steps. This is not a simple "double-click an exe" application; it is a Python-based server environment.

### Prerequisites
* **Python 3.10+**: Must be installed and accessible in your terminal. Ensure that Python and `pip` are added to your system PATH.
* **Git**: Required for cloning the repository and managing version updates.
* **Tesseract OCR (Required for the Scanner)**: The Optical Character Recognition engine used to read card text.
  * **Windows**: Download the [UB-Mannheim Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki). **CRITICAL:** During the installation wizard, you *must* check the box to "Add to PATH", or OpenYuGi will not be able to find the executable, resulting in scanner failure.
  * **Linux**: Run your standard package manager to install `tesseract-ocr`. (e.g., `sudo apt-get install tesseract-ocr`). You may also need `libtesseract-dev`.
  * **macOS**: Use homebrew to install tesseract: `brew install tesseract`.

### Step-by-Step Installation
1. **Clone the Repository:**
   Open your terminal or command prompt and clone the OpenYuGi repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/openyugi.git
   cd openyugi
   ```

2. **Set up a Virtual Environment (Highly Recommended):**
   To prevent conflicts with other Python projects, isolate OpenYuGi's dependencies in a virtual environment. This ensures your global python state remains clean.
   * **Windows:** Use `python -m venv venv` and activate it via `.\venv\Scripts\activate`
   * **Linux/macOS:** Use `python3 -m venv venv` and activate it via `source venv/bin/activate`

3. **Install Core Dependencies:**
   With your virtual environment activated, install the required Python packages. OpenYuGi uses a vast array of dependencies, from NiceGUI for the frontend to PyTorch for the AI engine.
   ```bash
   pip install -r requirements.txt
   ```
   *(Note for Linux users: The scanner heavily relies on `opencv-python` and machine learning libraries like `torch` and `doctr`. You may need to install additional system-level libraries such as `libgl1-mesa-glx` to satisfy OpenCV dependencies. If OpenCV fails to import, ensure your graphical subsystem libraries are up to date).*

4. **Launch the Server:**
   Start the application by running the main entry script. The server will initialize its background daemons, check for database updates, and spin up the ASGI web server.
   ```bash
   python main.py
   ```
   The application server will initialize, bind to your local machine (`127.0.0.1`), and automatically open your default web browser to `http://localhost:8080`.

---

## 📚 Documentation & The Knowledgebase

Detailed guides, tutorials, and deep architectural dives can be found in our **[Docs / Wiki](docs/Home.md)**.

The documentation is designed for both end-users and developers. It contains extensive explanations of the database schema structures, advanced UI modification tutorials, and detailed instructions on how to add custom banlists. If you encounter issues with the neural network scanner recognizing specific sets, the documentation also contains a robust troubleshooting guide for tuning computer vision parameters, adjusting perspective warp variables, and calibrating your webcam resolution.

If you are a developer looking to contribute, the documentation details the strict Model-View-Controller separation used in the source code, outlining how `src/services/` logic operates entirely independent of the `src/ui/` NiceGUI components.

---

## 📸 Deep Dive: The AI Scanner

The OpenYuGi AI Webcam Scanner is arguably its most powerful tool. It utilizes a sophisticated pipeline of Computer Vision techniques to process a live webcam feed and accurately identify physical cards in real-time, achieving accuracies comparable to commercial sorting machines.

### The Technical Pipeline
The scanner does not rely on a simple barcode or single-shot match. Instead, it operates using an event-driven state machine running on a background daemon (preventing the NiceGUI interface from freezing during heavy computation). The pipeline involves several distinct mathematical and neural network phases:

1. **Card Detection & Perspective Warp:** The system continuously analyzes the webcam feed for rectangular contours using a Canny edge detector and Hough line transforms. Once a card is detected against the background, it calculates the corners and applies a perspective warp (homography transformation) to mathematically "flatten" the card into a standard 2D plane, ensuring text is readable even if the card is held at a severe oblique angle. This allows the user to hold cards naturally without perfectly aligning them to the camera lens.
2. **Dual-Track OCR Engine:** The flattened image is passed to two simultaneous text recognition engines: **EasyOCR** and **DocTR**. These tracks work in parallel to scan specific Regions of Interest (ROIs): the bottom-right corner for the Set Code (e.g., LOB-EN001), the bottom-left for 8-digit Passcodes, and the top border for the Card Name. The dual-track system ensures that if one engine fails due to a smudge, micro-glare, or stylized font, the other acts as a fallback, significantly increasing the true-positive rate.
3. **Machine Vision Metadata Extraction:** While OCR handles the text, separate CV algorithms analyze visual metadata. The system checks specific regions of the card to detect Foil treatments (identifying Rarities like Secret Rare vs Super Rare by analyzing light reflection patterns and high-frequency noise variance) and looks for the presence of the golden "1st Edition" stamp in the bottom left corner using template matching.
4. **YOLO Art Classification Matching:** For cards where text is obscured or ambiguous (like Alternate Arts, where the passcode and set code might be identical but the art is completely different), the scanner computes a feature vector using a fine-tuned YOLOv8 classification model. It isolates the artwork box, extracts its latent features, and compares this vector against a heavily indexed local `data/images` database to find the closest visual match mathematically.
5. **Heuristic Candidate Resolution:** Finally, the scanner aggregates all data points and scores potential candidates using a weighted algorithm: Exact Set Code matches grant 80 points, Name string-similarity matches grant 50 points, and YOLO Art Style matches grant 40 points. The highest-scoring candidate that passes the minimum confidence threshold is presented to the user.

### Batch Commit Workflow
The scanner is not designed to add one card at a time. It uses a highly efficient "Batch Queue" system. You can sit down with a massive stack of 50 or 100 cards, scan them rapidly one by one, and they will populate a "Recent Scans" temporary pool array.

Once your entire stack is scanned, you can review the list, select multiple cards at once using shift-click, apply bulk modifiers (e.g., "Set all these highlighted cards to Lightly Played and German language"), and commit the entire batch to your JSON collection database simultaneously. This workflow turns hours of manual data entry into minutes.

### Best Practices & Things to Be Aware Of
* **Lighting is The Ultimate Bottleneck:** Glare from overhead lights on foil cards will completely blind the OCR engines and ruin the YOLO art matching by washing out the image tensor. You must ensure diffused, even, indirect lighting for the scanner to work efficiently. Avoid direct spotlights, ring lights pointing directly at the card, or scanning near bright sunny windows.
* **Background Contrast:** The edge-detection algorithm requires high contrast between the card edge and the background to calculate the bounding box. Use a dark, solid, non-reflective playmat (like a black cloth mat). A busy, patterned background (like a playmat with character art) will confuse the contour detection, resulting in the scanner failing to initiate the warp sequence entirely.
* **Ambiguity Handling:** Yu-Gi-Oh! sets are notoriously complex. Often, multiple rarities exist under the exact same Set Code (e.g., a set containing both an Ultra Rare and a Secret Rare version of the exact same card). When the scanner encounters this ambiguity, it pauses and prompts the UI to ask you to manually select the correct variant before adding it to the queue, ensuring your collection value remains accurate.
* **Hardware Demands:** Running dual OCR engines and a YOLOv8 neural network simultaneously is computationally expensive. While OpenYuGi is heavily optimized for CPU execution using quantization, older laptop hardware may experience a slight latency of 1-3 seconds per scan. If you possess a CUDA-enabled NVIDIA GPU, you can modify the scanner settings in the configuration file to leverage hardware acceleration (`torch.cuda`), reducing scan times to milliseconds.

---

## 🗃️ Data Architecture: Collections & Storage Explained

A core philosophy of OpenYuGi is absolute transparency. We want you to understand exactly how your data is structured so that you can back it up securely, write your own Python scripts against it, or modify it outside of the application interface if needed.

### The JSON Data Model
Your collections are not trapped in a monolithic SQL database file (like SQLite or PostgreSQL) or an opaque NoSQL format. Everything is stored in the `data/collections/` directory as beautifully formatted, plain-text JSON files.

Because JSON is universally supported, your data is inherently future-proof. You could literally open your collection in Notepad and read exactly what cards you own.

**You can have multiple collections.**
You are not limited to one massive database. You can create `Main_Binder.json`, `Trade_Binder.json`, `Goat_Format_Staples.json`, and `Bulk_Commons.json`. OpenYuGi handles these as entirely separate, isolated ecosystems. You can load whichever collection you want to work on from the top-left dropdown in the UI. This multi-tenant model means you can manage your personal stash separately from a friend's collection, or keep your low-value bulk strictly isolated from your high-end authenticated slabs.

### Collection Schema Deep Dive
The JSON structure is highly hierarchical, designed to aggregate data logically to minimize file size and maximize read/write speed. Every file undergoes strict Pydantic validation before being loaded into memory, ensuring corrupt data is caught instantly before it can crash the app.

Here is what a single card entry looks like inside your `collection.json`:

```json
{
  "card_id": 46986414,
  "name": "Blue-Eyes White Dragon",
  "variants": [
    {
      "set_code": "LOB-001",
      "rarity": "Ultra Rare",
      "entries": [
        {
          "quantity": 1,
          "condition": "Near Mint",
          "language": "EN",
          "first_edition": true,
          "storage_location": "Binder 1"
        },
        {
          "quantity": 3,
          "condition": "Lightly Played",
          "language": "DE",
          "first_edition": false,
          "storage_location": "Bulk Box A"
        }
      ]
    }
  ]
}
```
Notice the `entries` array. If you add another "Lightly Played, German, Unlimited" copy of the LOB Blue-Eyes, the system does not create a new massive object; it simply increments the `quantity` of the exactly matching entry from 3 to 4. This structural design ensures your JSON files remain extremely compact and incredibly fast to parse, even with tens of thousands of cards loaded into the NiceGUI state.

### Storage Locations
Within your collection, you can define physical storage structures. By navigating to the **Storage Tab**, you can create definitions like "Blue Binder", "Deck Box 1", or "Closet Bulk". When adding cards (either via the Bulk Add tab or the Scanner), you assign them to these predefined storage locations.

This ensures that a digital entry perfectly maps to a physical reality. When you need to find a specific tech card for a tournament on Friday night, you don't have to tear your room apart searching through every tin—OpenYuGi will tell you exactly which box it is in.

---

## 🏗️ Technical Deep Dives

### The Pro Deck Builder Architecture
The Deck Builder is not just a visual tool; it is a complex, validation-driven rules engine designed to perfectly mimic standard tournament constraints.
* **YDK Parsing**: When you import a `.ydk` file, the system parses the numerical passcodes line-by-line and cross-references them against the local `card_db.json`. It maps legacy codes seamlessly so that alternate arts load correctly without throwing ID resolution errors.
* **Banlist Engine**: The builder fetches the latest banlists directly from community repositories. It checks every card's ID against the current list upon insertion. If a card is limited to 1, and you add 2, the card border turns bright red. It even supports complex point-based restrictions for unofficial formats if you edit the backend config logic.
* **Side Deck Logic**: The builder explicitly separates Main, Extra, and Side deck zones. It understands that Fusion/Synchro/Xyz/Link monsters belong strictly in the Extra Deck and will automatically route them there when double-clicked, preventing illegal deck states. Moving cards between Main and Side decks is as simple as a drag-and-drop gesture using SortableJS event listeners.

### The Database Editor & API Integrations
OpenYuGi relies on the **YGOPRODeck API** to populate its initial reference data (`card_db.json`). However, APIs can be flawed, and they do not always support custom proxy sets or localized alternate rarities.
* **The DB Editor Tab**: This tool allows you to directly manipulate the `card_db.json` file. If a new set is released and the API hasn't updated its rarity distributions, you can manually add the rarity to the database yourself, preventing the app from rejecting valid inputs.
* **Custom Sets**: You can create entirely fabricated Set Codes (e.g., `CUSTOM-EN001`) for custom proxies or Oricas. Assign them to cards, and they will behave natively within the collection manager, allowing you to track custom prints exactly as if they were official Konami cards.
* **Yugipedia Integration**: For massive product imports (like importing a brand new Structure Deck), the backend utilizes Yugipedia parsing to ingest complete set lists automatically.

### Atomic Storage Moves
Data integrity is paramount in local-first apps. When moving a card from "Binder 1" to "Box 2", OpenYuGi utilizes an atomic `CollectionEditor` transaction. It ensures that the card is fully removed from the source location *before* it is added to the destination array. If the application crashes midway due to a power outage, the transaction rolls back via deep-copy state management, ensuring you never accidentally duplicate or delete cards during massive bulk moves. Every change is logged to an internal changelog manager for absolute safety.

### UI Rendering Optimization (NiceGUI)
Because traditional Vue/React setups are bulky, OpenYuGi uses NiceGUI (which builds on Vue under the hood but executes entirely via Python state). To prevent the browser from freezing when displaying a collection of 50,000 cards:
* **Lazy Image Binding**: The `ImageManager` intercepts UI rendering calls and only loads the `.jpg` into the DOM when the card row scrolls into the viewport.
* **Debounced Event Listeners**: Typing into the filter bar does not execute a 50,000-item array iteration on every keystroke. The inputs are debounced by 300ms, ensuring your CPU is only taxed when you finish typing.

---

## 🛠️ Troubleshooting & FAQ

**Q: "ModuleNotFoundError: No module named 'src'"**
*   **Cause**: You attempted to run the server from within the `src` directory (e.g., `python src/main.py`). The Python pathing requires execution from the root.
*   **Fix**: Always run the application from the root directory using `python main.py`.

**Q: The Scanner is disabled or crashing immediately upon opening the tab.**
*   **Cause**: You likely did not install Tesseract OCR correctly, or you failed to check the "Add to PATH" option during installation on Windows. The python subprocess cannot locate the `tesseract` binary.
*   **Fix**: Reinstall Tesseract and ensure your system PATH variables are updated. You can verify this by typing `tesseract --version` in your terminal. Ensure the executable exists at `C:\Program Files\Tesseract-OCR\tesseract.exe`.

**Q: The application interface freezes when I upload a massive CSV or JSON backup.**
*   **Cause**: Browsers struggle with uploading massive payloads synchronously over WebSockets.
*   **Fix**: Be patient. OpenYuGi processes massive I/O operations asynchronously on the backend to protect the event loop using `run.io_bound(...)`, but the browser UI may hang for a few seconds while the file is parsed by Pydantic and rendered back to the DOM.

**Q: Images are showing up as broken links or placeholders.**
*   **Cause**: OpenYuGi uses a lazy-loading image manager. It downloads images from the YGOPRODeck API the first time they are requested by the UI. If you have no internet connection, or if the API is rate-limiting you, images will fail to load and return 404s to the frontend.
*   **Fix**: Ensure your internet connection is active. Check the `data/images/` directory to see if `.jpg` files are actually populating. If not, wait 15 minutes and try again to clear any API rate limits.

**Q: Does OpenYuGi support Rush Duel or Speed Duel formats?**
*   **Answer**: Speed Duel cards are natively integrated into the master database and can be tracked normally. Rush Duel cards are currently dependent on external API support and may not be fully represented in the local cache, requiring manual addition via the DB Editor.

**Q: Can I run this on a Raspberry Pi or low-power NAS?**
*   **Answer**: Yes, the core collection manager will run smoothly. However, the AI webcam scanner requires significant computational power. If you run OpenYuGi on a Pi, you should disable the scanner module or expect extremely slow scan times (10-20 seconds per card) due to the heavy PyTorch/YOLO CPU tensor requirements.

**Q: My JSON collection file got corrupted when my computer crashed. What do I do?**
*   **Answer**: OpenYuGi automatically manages backups. Navigate to your `data/collections/backups/` directory. You will find timestamped copies of your JSON files from previous successful sessions. Simply replace your corrupted main JSON file with the most recent backup.

**Q: Why does the Scanner misread Ghost Rares?**
*   **Answer**: Ghost Rares possess a unique holofoil treatment that strips contrast from the art box and creates extreme glare. The YOLO Art matching model cannot process the washed-out tensor. You will need to rely entirely on the OCR engines reading the Set Code, or enter Ghost Rares manually via the Browse Sets tab.

**Q: I have a massive Cardmarket inventory. Can I import it?**
*   **Answer**: Yes. Use the Import Tools tab. OpenYuGi natively parses standard Cardmarket Stock `.txt` files and `.csv` files, mapping the distinct language and condition abbreviations (like "EX" for Excellent) directly into internal Pydantic models.

---

## 🗃️ Exhaustive Feature List

* **Fully Offline Operation**: Zero reliance on internet access for core functionality.
* **Multi-Collection Support**: Maintain isolated JSON files for trades, personal collections, and bulk.
* **Pydantic Validation**: Strict internal data typing ensures your JSON files never become corrupted or invalid.
* **Granular Variant Tracking**: Support for Set Code, Rarity, Condition (Mint to Damaged), Language (with dedicated visual flags), and Edition (1st, Unlimited, Limited).
* **Consolidated vs Specific Views**: Toggle between base-card aggregations and specific variant listings.
* **Lazy Image Loading**: Supports loading thousands of high-res card arts without crashing the browser or running out of RAM.
* **Advanced Filter Engine**: Filter by Name, Set Code, Rarity, Attribute, Type, Level/Rank/Link Rating, Pendulum Scale, and specific Storage Containers.
* **SortableJS Drag-and-Drop**: Modern frontend interaction for moving cards between storage or adding from search.
* **Physical Storage Definitions**: Create unlimited custom Binders, Boxes, and Tins.
* **Atomic Move Operations**: Safely transfer cards between physical storage locations with guaranteed database consistency.
* **Visual Storage Gallery**: Graphical representation of your physical storage with live count indicators.
* **Pro Deck Builder Sandbox**: Drag-and-drop interface for Main, Side, and Extra decks.
* **Live Banlist Checking**: Dynamic validation against TCG Advanced, OCG, and Time-Wizard (Edison/Goat) formats.
* **Collection Cross-Referencing**: Deck builder shows exact physical ownership counts for every card added.
* **Standard `.ydk` Compatibility**: Import and Export decks directly to YGOOmega, EDOPro, and other simulators.
* **AI Webcam OCR Scanner**: Real-time perspective warping and dual-track text recognition (EasyOCR/DocTR).
* **YOLOv8 Art Classification**: Neural network matching for alternate arts and obscured text.
* **Scanner Batch Queuing**: Scan dozens of cards into a temporary queue, edit them in bulk, and commit them instantly.
* **Ambiguity Prompting**: System halts and asks for manual input when sets contain identical codes across different rarities.
* **Scanner Debug Lab**: Developer tools to visualize edge detection parameters and cropped Region-Of-Interest images.
* **Cardmarket Format Import**: Native parsing for standard Cardmarket stock files (`.txt` and `.pdf`).
* **JSON Backup System**: Built-in snapshot capabilities for safe editing.
* **CSV Reporting**: Export collections to Excel-friendly formats for trading or record keeping.
* **Local Database Editor**: Manually override official API card stats or create custom proxy set codes.
* **Responsive NiceGUI Design**: Scales cleanly across massive 4K monitors and standard laptop displays using Tailwind CSS.
* **Undo Functionality for Bulk Imports**: Roll back massive database changes with integrated changelog managers.
* **Database Cache System**: Downloads and stores the entire YGOPRODeck API response locally for instantaneous searching.
* **Art Crop Caching**: Automatically downloads and crops card art locally for faster visual matching and gallery displays.
* **Country Flag Visualization**: UI assigns distinct flag icons to cards based on their language variant for quick visual parsing.
* **Changelog Auditing**: Built-in changelog tracker to revert or audit mass edits across bulk additions.
* **Custom Set Code Injection**: Ability to define localized Set Codes for unofficial printings without breaking the core engine.
* **Real-time Master Set Tracking**: Visual completion percentage tracking for every canonical Konami release.
* **Automated Data Type Enforcement**: Ensures that condition arrays and language arrays strictly conform to project standards.
* **Mobile-Responsive Containers**: Uses Tailwind CSS classes to dynamically reflow data grids from 1 column on mobile to 12 columns on 4K ultrawides.
* **Multi-Threaded CV Pipeline**: Pushes YOLO and OCR calculations into daemon threads to prevent the UI from freezing during intensive processing.
* **Dynamic Set Ambiguity Resolution**: Evaluates region codes (EN vs DE vs generic) dynamically to auto-select the most likely intended card variant during ambiguous scans.
* **Recursive Folder Management**: Safely generates its own filesystem environment (`data/collections/`, `data/images/`, `data/db/`) on the first run without user intervention.
* **Event-Driven Subsystems**: Communication between the backend daemon and frontend browser using custom NiceGUI event emitters.
* **No Telemetry Constraints**: Guaranteed zero tracking, zero ad-injecting, and zero "phoning home".
* **Comprehensive Logging**: Detailed internal logging system (`data/logs/`) for debugging API failures and OCR timeouts.
* **Offline Fallback Mechanisms**: If external APIs fail, the system gracefully falls back to cached `.json` values.
* **Strict Type Hinting**: Entire codebase is fully typed, allowing developers to easily extend functionality with full autocomplete support.
* **Minimal External Bloat**: Uses native Python libraries wherever possible to minimize install footprint and reduce attack surfaces.
* **Debounced Event Listeners**: Search bars and filters use strict millisecond debouncing to save CPU cycles during rapid user input.
* **Hardware Acceleration Hooks**: Built-in hooks in the config file to transition the PyTorch model from CPU execution to CUDA/MPS arrays for instant scanning.
* **Dynamic Chart Rendering**: Recharts arrays directly from database lookups for statistical tracking of deck ratios.
* **Yugipedia Web Scraping**: Integrates BeautifulSoup parsers for pulling live structure deck sets instantly when official APIs lag behind real-world releases.
* **In-Memory Cache Coherency**: Syncs the visual NiceGUI DOM layer explicitly with the underlying Pydantic data model without relying on dirty checking loops.
* **Regex Driven Bulk Updates**: Complex Regex is utilized across bulk add menus to instantly transform dirty text input into correctly typed Enums.
* **Deep Copy Reversion**: Every mass operation creates a deeply copied clone of the state, allowing the system to instantly revert 10,000 bad insertions back to absolute zero in microseconds.

## 🔍 Advanced Customization & Scripting

OpenYuGi is explicitly designed to be hacker-friendly. Because your data is entirely local and decoupled from a proprietary backend server, power users can heavily script and automate operations.

### Scripting Against the Database
Since your collections are purely JSON, you can interact with them using native Python without ever booting the web application.

Here is a simple example script you could write to find every 1st Edition Ultimate Rare you own across all collections:

```python
import json
import os
import glob

def find_first_ed_ultis():
    collection_dir = "data/collections/"
    found_cards = []

    for file in glob.glob(os.path.join(collection_dir, "*.json")):
        with open(file, 'r') as f:
            data = json.load(f)

            # Navigate the JSON Hierarchy
            for card in data.get("cards", []):
                for variant in card.get("variants", []):
                    if variant.get("rarity") == "Ultimate Rare":
                        for entry in variant.get("entries", []):
                            if entry.get("first_edition") == True:
                                found_cards.append({
                                    "name": card["name"],
                                    "set": variant["set_code"],
                                    "quantity": entry["quantity"],
                                    "location": entry["storage_location"]
                                })

    return found_cards

if __name__ == "__main__":
    results = find_first_ed_ultis()
    for item in results:
        print(f"Found {item['quantity']}x {item['name']} ({item['set']}) in {item['location']}")
```

### Modifying the Banlist Logic
OpenYuGi fetches banlists dynamically, but tournament environments are highly variable. If you run a local retro format (like perfectly simulated 2011 Tengu Plant format), you can intercept the banlist logic.

Navigate to `src/services/banlist_service.py`. The system pulls data from external URLs, but you can override the `_load_banlist` method to read a local `custom_banlist.json` file. The engine will instantly propagate your custom restrictions across the entire Deck Builder UI, flagging any cards that violate your localized constraints.

### Tweaking the Machine Vision Parameters
Computer vision is an art. If your webcam has a strange focal length or your room has specific spectral lighting that is breaking the scanner, you can modify the core CV parameters.

Navigate to `src/services/scanner/pipeline.py`. Within this file, you can adjust:
*   **Canny Edge Thresholds:** Increase or decrease the strictness of the edge detector. If your background mat is noisy, increasing the threshold will force the scanner to only look for incredibly hard lines.
*   **Contour Area Minimums:** If the scanner is triggering on small rectangles (like the art box instead of the card border), you can increase the `min_contour_area` to force it to only recognize large physical objects.
*   **Warp Dilation:** When the homography warp executes, it applies a slight dilation to cut off the physical card edges so they don't interfere with OCR. You can increase this `margin` if your camera creates a fisheye effect around the edges.

### Extending the Database Editor
The DB Editor currently allows basic manipulation of Atk, Def, Level, and Type. Because the local cache (`data/db/card_db.json`) perfectly mirrors the official API architecture, you can write scripts to completely overwrite this cache.

If you want to create an entire custom cube of cards based on an anime series, you can format a JSON array mimicking the standard API response, inject it into the `card_db.json`, and the entire frontend (from the Deck Builder to the Search UI) will immediately recognize your custom cards without requiring any HTML or Javascript modifications.

---

## 🏗️ The Application State Machine
For contributors, it is critical to understand how OpenYuGi handles state. Unlike React, which relies on a Virtual DOM, or standard Python Flask, which is entirely stateless, OpenYuGi utilizes a continuous ASGI websocket loop via NiceGUI.

When you click "Add Card", the sequence is:
1. The Vue frontend fires an event to the websocket.
2. The Python handler `handle_add_card` receives the event asynchronously.
3. The method calls the `CollectionEditor` service, which isolates the database write operation.
4. The JSON file is overwritten atomically using `orjson`.
5. The `CollectionEditor` signals success back to the UI view model.
6. The UI view model triggers a `ui.refresh()` decorator.
7. The Python server recalculates the specific HTML fragments for that specific component and pushes the diff back over the websocket to the browser.

This precise loop ensures that you can safely open the application in multiple browser tabs simultaneously without corrupting the underlying JSON state, as all writes are serialized through the Python backend loop.

---

## 🖥️ Server Deployment Notes
While OpenYuGi is designed primarily as a local desktop application (accessed via `localhost`), it is structurally a full web server.

If you wish to host OpenYuGi on a local network attached storage (NAS) device or a home lab server so you can access your collection from your mobile phone while at a tournament:
1. Bind the application to your local network IP by modifying the `ui.run()` command in `main.py`: `ui.run(host='0.0.0.0', port=8080)`.
2. Access the application on your phone by navigating to the server's IP address (e.g., `http://192.168.1.100:8080`).
3. **Security Warning:** OpenYuGi does *not* possess user authentication. It is not designed to be exposed to the public internet. If you port-forward this application, anyone who finds the IP will have full read/write access to your JSON collection database. Always run it behind a VPN (like Tailscale or Wireguard) if you need remote access outside your home network.

---

## 📈 Roadmap & Future Development
Because OpenYuGi is open source, its future is dictated entirely by the needs of its power users. Current architectural goals include:

*   **Offline Pricing Index:** Expanding the JSON engine to cache historic pricing data locally, allowing users to view 1-year value charts entirely offline without triggering API rate limits.
*   **WebRTC Remote Webcam:** Developing a module to allow users to use their smartphone's high-quality camera as the scanner input for the desktop application over a local WebRTC connection.
*   **Custom Format Support:** Formalizing the custom banlist logic into the NiceGUI frontend, allowing users to create, share, and validate against user-generated "Cube" or "Progression" series formats dynamically.

---

*Built with absolute dedication to data sovereignty by the OpenYuGi community. Never rent your data.*

## 🧩 Modding the User Interface
OpenYuGi's UI is written entirely in Python utilizing the NiceGUI framework, which wraps Vue 3 and Tailwind CSS. This means you do not need to know Javascript, HTML, or CSS to modify the look and feel of the application.

If you find the default data grid too dense, or you want to add a custom "Notes" field to every card view, you can do so natively in Python.

### Example: Adding a Custom UI Element
Navigate to `src/ui/components/single_card_view.py`. This file controls how a card is rendered in the Collector View mode.

If you want to inject a custom button next to the card name that triggers a print action, you simply find the layout row and add:

```python
from nicegui import ui

# Inside the render loop:
with ui.row().classes('items-center justify-between w-full'):
    ui.label(self.card.name).classes('text-xl font-bold')

    # Your Custom Button
    ui.button('Print Proxy', on_click=lambda: self._trigger_local_print(self.card)) \
      .props('outline rounded color="purple"') \
      .tooltip('Send this card art to the default local printer')
```

Because the framework automatically compiles this Python down into a reactive Vue component, your new button will instantly appear and respond to clicks without needing to rebuild a webpack bundle or manage node modules.

### Customizing the Theme
OpenYuGi uses Tailwind CSS utility classes heavily. If you wish to change the entire color scheme (for example, switching the accent color from standard blue to dark mode crimson), you can modify the global configuration located in `src/ui/theme.py`.

The theme file defines the primary, secondary, and accent colors injected into the Quasar engine at startup.

```python
# src/ui/theme.py
def apply_theme():
    ui.colors(
        primary='#b91c1c',     # Crimson Red Primary
        secondary='#1f2937',   # Slate Gray Secondary
        accent='#f59e0b',      # Amber Accent
        dark='#111827',        # Deep Background
        positive='#10b981',    # Success Green
        negative='#ef4444',    # Error Red
        info='#3b82f6',        # Info Blue
        warning='#f59e0b'      # Warning Orange
    )
```

## 🗄️ Database Backup Automation
Because OpenYuGi operates strictly via local files, maintaining a robust backup strategy is paramount. While the application automatically creates snapshot backups during session transitions, power users should implement external version control.

### Using Git for Collection Versioning
The most robust way to manage your JSON collection is by initializing a Git repository specifically for your `data/collections/` directory.

1. Navigate to the directory: `cd data/collections`
2. Initialize Git: `git init`
3. Add the files: `git add .`
4. Commit your initial state: `git commit -m "Baseline Collection"`

By tracking your JSON files with Git, you gain an immutable, cryptographically secure history of every change you've ever made. If you accidentally delete a binder, or if you want to see exactly what cards you traded away on March 15th, 2022, you can use standard `git diff` commands to instantly visualize the delta between states.

### Automating Backups with Cron (Linux/macOS)
If you are running OpenYuGi on a Unix-based system, you can automate your backups effortlessly using `cron`.

Open your crontab: `crontab -e`

Add the following line to zip your entire data directory and store it in an external drive at 2:00 AM every single night:
```bash
0 2 * * * zip -r /mnt/external_drive/backups/openyugi_$(date +\%F).zip /path/to/openyugi/data/
```

## ⚙️ Advanced System Tuning

### Disk I/O Bottlenecks
When loading collections exceeding 100,000 cards, the primary bottleneck will shift from CPU parsing to Disk I/O. Traditional hard drives (HDDs) may experience micro-stutters when saving the massive JSON files.
*   **Recommendation:** Always run OpenYuGi on a Solid State Drive (NVMe SSD preferred). The rapid read/write speeds ensure that the simulated atomic overwrites occur in milliseconds, preventing any UI hang.

### RAM Allocation
Python's memory management handles the JSON translation gracefully. A typical 20,000 card collection requires approximately 150MB of RAM to keep fully active in memory via the Pydantic models.
*   **Recommendation:** If you are running multiple custom Python scripts concurrently against the database while the server is active, ensure you have at least 2GB of available system RAM to prevent swapping.

### OpenCV Video Capture Backends
Different operating systems handle webcam feeds differently. If you experience massive latency in the AI Scanner Tab video feed (e.g., the video updates at 5 Frames Per Second), the issue is likely the default OpenCV video backend.
*   **Windows Fix:** Modify the `cv2.VideoCapture(0)` call in `src/services/scanner/manager.py` to use DirectShow explicitly: `cv2.VideoCapture(0, cv2.CAP_DSHOW)`.
*   **Linux Fix:** Ensure `v4l2` is installed and change the capture flag to `cv2.CAP_V4L2`.

---


## 📜 Licensing & Open Source Philosophy

OpenYuGi is released under the **MIT License**. This permissive license guarantees that the software is free, and will remain free, forever. You are permitted to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software without restriction.

We chose the MIT License over restrictive copyleft licenses like GPL to ensure that local game stores (LGS) or professional vendors can utilize the OpenYuGi core engine, or components like the AI Scanner, in their own internal inventory tools without being legally compelled to open-source their proprietary POS systems.

**Our Philosophy:** The tools to manage your own property should not be gated behind subscription models. Data related to your physical assets should reside exclusively on hardware you physically own.

## 🤝 Contributing to OpenYuGi

As a massive, community-driven project, OpenYuGi thrives on contributions from developers, computer vision enthusiasts, and hardcore Yugioh judges.

If you wish to contribute, please follow this standardized workflow:
1.  **Fork the Repository:** Create your own instance of the project on GitHub.
2.  **Create a Feature Branch:** Branch off of `main` with a descriptive name (e.g., `git checkout -b feature/implement-rush-duel-support`).
3.  **Adhere to Architecture Guidelines:** Read `AGENTS.md` and the Technical Documentation carefully. Ensure that your business logic remains strictly within `src/services/` and that your UI components in `src/ui/` do not directly mutate database state.
4.  **Write Tests:** OpenYuGi utilizes `pytest`. Ensure that any new parser or validation logic is covered by unit tests in the `tests/` directory. If you are modifying UI components, use Playwright to verify the visual state.
5.  **Commit with Conventional Messages:** Use standard prefixes like `feat:`, `fix:`, or `docs:` for clarity.
6.  **Open a Pull Request:** Submit your PR against the main repository. Ensure your PR description clearly outlines the problem solved and links to any relevant issues.

*Thank you for taking control of your data with OpenYuGi.*
