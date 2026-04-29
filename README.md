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

The LLM will extract everything it needs from the comprehensive architecture details and setup instructions below to generate a tailored script specifically for your operating system and environment. Because OpenYuGi relies heavily on local hardware integration for its AI scanner, an LLM can save you significant time by generating platform-specific environment variables and package manager commands.

---

## 📖 TL;DR: What is OpenYuGi?

**OpenYuGi** is a professional-grade, locally-hosted, privacy-focused Yugioh collection manager, built specifically for serious collectors, tournament players, and data-minded individuals.

In an era where every application demands an account, a subscription, and constant cloud synchronization, OpenYuGi takes a radical stance: **Your Data, Your Drive.**

Instead of locking your data behind proprietary servers, OpenYuGi stores your entire collection as readable, plain-text JSON files right on your hard drive. It features an incredibly fast modern UI powered by Python's NiceGUI, massive bulk-operation capabilities, an extensive Pro Deck Builder that validates against competitive formats, and a state-of-the-art AI-powered webcam scanner.

Whether you are cataloging a massive bulk pile of tens of thousands of cards or meticulously curating a high-end Goat Format binder, OpenYuGi is designed to handle immense scale entirely offline, without lag, and without telemetry.

---

## ✨ Salient Features & Advantages

### For The Serious Collector:
* **Absolute Privacy & Data Ownership:** Your collection is yours. Because everything is stored locally in human-readable JSON files, you are never locked out of your own inventory. If OpenYuGi ceases development tomorrow, your data is completely safe and accessible.
* **Infinite Granularity & Variant Tracking:** Most collection managers treat a "Blue-Eyes White Dragon" as a single entity. OpenYuGi allows you to track an infinite number of distinct variants. You can track exact set codes, 1st Edition vs Unlimited, specific languages, and specific conditions.
* **Collector vs. Player View Toggle:** OpenYuGi understands that players and collectors look at cards differently. The UI allows you to toggle instantly between viewing consolidated playsets (Player Mode - "I have 5 Mystical Space Typhoons across various sets") and distinct physical printings (Collector Mode - "I have two SDK-001 Commons and three MRL-047 Secret Rares").
* **Physical Storage Emulation:** Create unlimited custom "Binders" and "Boxes" within the application. You can assign individual cards to these digital storage containers, ensuring you always know exactly which physical box under your bed contains your specific tech cards.

### For The Competitive Player:
* **Tournament-Ready Pro Deck Builder:** A comprehensive deck-building interface that rivals dedicated simulators. It dynamically validates your deck against current Advanced TCG, OCG, and historical formats like Goat Format.
* **Real-Time Physical Cross-Referencing:** As you build a deck, OpenYuGi actively checks your local JSON collection database. If you add three "Ash Blossom & Joyous Spring" to your list, the builder will visually indicate if you actually own three physical copies, or if you only own two and need to proxy/purchase a third.
* **YDK Interoperability:** Full support for standard `.ydk` files. You can export your decks straight from OpenYuGi to your favorite online simulators like EDOPro, YGOOmega, or Duelingbook without manual transcription.
* **No Telemetry, No Lag:** Because everything runs entirely locally on your own machine, filtering and searching through tens of thousands of cards is instantaneous. You never have to wait on a server to respond to a search query.

### For The Data Hoarder:
* **AI Webcam Scanner Digitization:** Digitize entire piles of cards in minutes using the built-in webcam scanner. The scanner leverages advanced neural networks and OCR to read set codes, match card art, and automatically queue them into a batch for mass addition to your database.
* **Bulk Import and Data Portability:** Seamlessly move large quantities of data in and out of the system. Import raw stock files, perform massive drag-and-drop operations, and export everything to CSV for external spreadsheet analysis.
* **Database Editor:** Sometimes official APIs are wrong, or you have a custom proxy. OpenYuGi includes a built-in Database Editor, allowing you to manually override card statistics, fix rarities, or even build entirely custom proxy sets locally.

---

## 🚀 Installation & Setup Guide

Because OpenYuGi relies on local machine learning models for its scanner, setting up the environment requires a few specific steps.

### Prerequisites
* **Python 3.10+**: Must be installed and accessible in your terminal. Ensure that Python and `pip` are added to your system PATH.
* **Tesseract OCR (Required for the Scanner)**: The Optical Character Recognition engine used to read card text.
  * **Windows**: Download the [UB-Mannheim Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki). **CRITICAL:** During the installation wizard, you *must* check the box to "Add to PATH", or OpenYuGi will not be able to find the executable.
  * **Linux**: Run your standard package manager to install `tesseract-ocr`. (e.g., `sudo apt-get install tesseract-ocr`).
  * **macOS**: Use homebrew to install tesseract: `brew install tesseract`.

### Step-by-Step Installation
1. **Clone the Repository:**
   Open your terminal or command prompt and clone the OpenYuGi repository to your local machine.
2. **Set up a Virtual Environment (Highly Recommended):**
   To prevent conflicts with other Python projects, isolate OpenYuGi's dependencies in a virtual environment (e.g., standard python venv module).
3. **Install Core Dependencies:**
   With your virtual environment activated, install the required Python packages using pip against `requirements.txt`.
   *(Note for Linux users: The scanner heavily relies on `opencv-python` and machine learning libraries like `torch` and `doctr`. You may need to install additional system-level libraries such as `libgl1-mesa-glx` to satisfy OpenCV dependencies).*
4. **Launch the Server:**
   Start the application by running the main entry script: `python main.py`.
   The application server will initialize, bind to your local machine, and automatically open your default web browser to `http://localhost:8080`.

---

## 📚 Documentation & The Knowledgebase

Detailed guides, tutorials, and deep architectural dives can be found in our **[Docs / Wiki](docs/Home.md)**.

The documentation is designed for both end-users and developers. It contains extensive explanations of the database schema structures, advanced UI modification tutorials, and detailed instructions on how to add custom banlists. If you encounter issues with the neural network scanner recognizing specific sets, the documentation also contains a robust troubleshooting guide for tuning computer vision parameters.

---

## 📸 Deep Dive: The AI Scanner

The OpenYuGi AI Webcam Scanner is arguably its most powerful tool. It utilizes a sophisticated pipeline of Computer Vision techniques to process a live webcam feed and accurately identify physical cards in real-time.

### The Technical Pipeline
The scanner does not rely on a simple barcode or single-shot match. Instead, it operates using an event-driven state machine running on a background daemon (preventing the NiceGUI interface from freezing during heavy computation). The pipeline involves:

1. **Card Detection & Perspective Warp:** The system continuously analyzes the webcam feed for rectangular contours. Once a card is detected against the background, it calculates the corners and applies a perspective warp to mathematically "flatten" the card, ensuring text is readable even if the card is held at an angle.
2. **Dual-Track OCR Engine:** The flattened image is passed to two simultaneous text recognition engines: **EasyOCR** and **DocTR**. These tracks work in parallel to scan the bottom-right corner for the Set Code (e.g., LOB-EN001), the bottom-left for Passcodes, and the top border for the Card Name.
3. **Machine Vision Metadata Extraction:** While OCR handles the text, separate CV algorithms analyze visual metadata. The system checks specific regions of the card to detect Foil treatments (identifying Rarities like Secret Rare vs Super Rare) and looks for the presence of the golden "1st Edition" stamp.
4. **YOLO Art Classification Matching:** For cards where text is obscured or ambiguous (like Alternate Arts), the scanner computes a feature vector using a fine-tuned YOLOv8 classification model. It compares this vector against a heavily indexed local `data/images` database to find the closest visual match.
5. **Heuristic Candidate Resolution:** Finally, the scanner scores all potential candidates using a weighted algorithm: Set Code matches grant 80 points, Name matches grant 50 points, and Art Style matches grant 40 points. The highest-scoring candidate is presented to the user.

### Batch Commit Workflow
The scanner is not designed to add one card at a time. It uses a "Batch Queue" system. You can sit down with a stack of 50 cards, scan them rapidly one by one, and they will populate a "Recent Scans" temporary pool.

Once your stack is scanned, you can review the list, select multiple cards at once, apply bulk modifiers (e.g., "Set all these to Lightly Played and German"), and commit the entire batch to your collection database simultaneously.

### Best Practices & Things to Be Aware Of
* **Lighting is The Ultimate Bottleneck:** Glare from overhead lights on foil cards will completely blind the OCR engines and ruin the YOLO art matching. You must ensure diffused, even, indirect lighting for the scanner to work efficiently.
* **Background Contrast:** The edge-detection algorithm requires contrast. Use a dark, solid, non-reflective playmat (like a black cloth mat). A busy, patterned background will confuse the contour detection.
* **Ambiguity Handling:** Yu-Gi-Oh! sets are notoriously complex. Often, multiple rarities exist under the exact same Set Code (e.g., a set containing both an Ultra Rare and a Secret Rare version of the same card). When the scanner encounters this ambiguity, it pauses and prompts the UI to ask you to manually select the correct variant before adding it to the queue.
* **Hardware Demands:** Running dual OCR engines and YOLOv8 simultaneously is computationally expensive. While OpenYuGi is heavily optimized for CPU execution, older hardware may experience a slight latency of 1-3 seconds per scan.

---

## 🗃️ Data Architecture: Collections & Storage Explained

A core philosophy of OpenYuGi is transparency. We want you to understand exactly how your data is structured.

### The JSON Data Model
Your collections are not trapped in a monolithic SQL database file. Everything is stored in the `data/collections/` directory as beautifully formatted JSON files.

**You can have multiple collections.**
You are not limited to one massive database. You can create `Main_Binder.json`, `Trade_Binder.json`, `Goat_Format_Staples.json`, and `Bulk_Commons.json`. OpenYuGi handles these as entirely separate ecosystems. You can load whichever collection you want to work on from the top-left dropdown in the UI.

### Collection Schema Deep Dive
The JSON structure is highly hierarchical, designed to aggregate data logically. Here is what a single card entry looks like inside your `collection.json`:

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
Notice the `entries` array. If you add another "Lightly Played, German, Unlimited" copy of the LOB Blue-Eyes, the system does not create a new massive object; it simply increments the `quantity` of the matching entry from 3 to 4. This ensures your JSON files remain extremely compact and incredibly fast to parse, even with tens of thousands of cards.

### Storage Locations
Within your collection, you can define physical storage structures. By navigating to the **Storage Tab**, you can create definitions like "Blue Binder", "Deck Box 1", or "Closet Bulk". When adding cards, you assign them to these storage locations. This ensures that a digital entry perfectly maps to a physical reality.

---

## 🧭 Navigating the OpenYuGi Interface

OpenYuGi is divided into several powerful tabs, accessible from the main navigation sidebar.

### Dashboard
The central hub. It provides an at-a-glance overview of your currently loaded collection, displaying total card counts, unique variants, and quick-access shortcuts to your most recently edited decks and recently added cards.

### Collection Tab
The main viewing area for your inventory.
* Contains the massive data grid that supports lazy loading for thousands of images.
* Features a robust **Filter Pane** that allows complex queries (e.g., "Show me only WATER attribute monsters, between Level 4 and 6, that I own at least 3 copies of, from the Labyrinth of Nightmare set").
* Houses the toggle for **Player View** (consolidated) vs **Collector View** (expanded printings).

### Browse Sets
A tool dedicated to exploring official Yu-Gi-Oh! releases.
* View every set ever released chronologically.
* Click into a set to see its entire card roster.
* The UI color-codes cards you own within the set, providing a visual "completion percentage" for collectors attempting to complete master sets.

### Storage Management
A visual, gallery-style interface representing your physical inventory.
* View all defined Binders and Boxes.
* See exactly how many cards are inside a specific binder.
* You can click into a binder to view its contents, and easily move cards between storage locations using a streamlined transfer interface.

### Deck Builder
A professional sandbox for creating `.ydk` format decks.
* **Visual Grid:** Drag and drop cards from a massive searchable library into your Main, Extra, and Side decks.
* **Banlist Enforcer:** Toggle between standard advanced formats, OCG lists, or historical Time-Wizard lists (Goat, Edison). Cards violating the list are aggressively highlighted in red.
* **Collection Sync:** A dynamic counter hovers over every card in your decklist, pulling live data from your JSON collection. If you add a 3rd copy of "Pot of Duality" but only own 2, the counter will turn orange to warn you of the discrepancy.

### Bulk Add & Drag-and-Drop
Designed for entering massive decklists or purchased lots.
* Features a split-pane layout: Search library on the left, your collection on the right.
* Uses SortableJS to allow you to literally drag massive lists of cards from search results into your database.
* Includes a massive "Batch Update" panel allowing you to assign Languages, Conditions, and Storage locations to hundreds of highlighted cards simultaneously.

### Import / Export Tools
The gateway for data migration.
* **CSV Export:** Generate spreadsheet dumps for external analysis or sharing.
* **JSON Backup / Restore:** Create safe snapshots of your collections before making massive edits.
* **Raw Text Import:** Paste decklists or raw string data and watch OpenYuGi parse it into actual database entries.

### Scan Tab
The interface for the AI Webcam scanner mentioned above. Features live webcam feeds, real-time bounding box overlays, and the temporary batch queue for review before committing to the main database.

### DB Editor (Database Editor)
A developer/power-user tool. It allows you to directly interface with the local cached `card_db.json`. You can fix incorrect API data, adjust specific card attributes, or define custom Set Codes for proxy cards that don't exist in official databases.

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
