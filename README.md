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

The LLM will extract everything it needs from the comprehensive architecture details and setup instructions below to generate a tailored script specifically for your operating system and environment.

---

## 📖 TL;DR: What is OpenYuGi?

**OpenYuGi** is a professional-grade, locally-hosted, privacy-focused Yugioh collection manager, built specifically for serious collectors, tournament players, and data-minded individuals.

Instead of locking your data behind accounts, subscriptions, or cloud servers, OpenYuGi stores your entire collection as readable, plain-text JSON files right on your hard drive. It features an incredibly fast modern UI powered by Python's NiceGUI, massive bulk-operation capabilities, external market integration, a tournament-ready Deck Builder, and a state-of-the-art AI-powered webcam scanner.

**Your Data. Your Rules. Completely Offline.**

---

## ✨ Salient Features & Advantages

For Collectors:
* **Absolute Privacy & Data Ownership:** Your collection is yours. Stored in human-readable JSON files, ensuring you are never locked out of your own inventory.
* **Granular Organization:** Track every single variant (Set Code, Edition, Language, Condition) across an infinite number of binders and boxes.
* **Real-time Market Valuation:** Automated integration with Cardmarket and TCGPlayer gives instant, actionable value to your cards without scraping sites yourself.
* **Collector vs. Player Views:** Toggle instantly between viewing consolidated playsets (Player Mode) and distinct, specific physical printings (Collector Mode).

For Players:
* **Pro Deck Builder:** A comprehensive tool that dynamically validates against TCG, OCG, and Goat banlists, while cross-referencing your actual physical inventory so you know exactly what you own.
* **YDK Interoperability:** Full support for `.ydk` files. Export your decks straight to EDOPro, YGOOmega, or Dueling Nexus.
* **AI Webcam Scanner:** Rapidly digitize bulk piles or new purchases by just pointing your camera at them, complete with batch-commit workflows.
* **No Telemetry, No Lag:** Everything runs entirely locally. Instant filtering of thousands of cards without waiting on a server response.

---

## 🚀 Installation & Setup

### Prerequisites
* **Python 3.10+**: Must be installed and accessible in your terminal.
* **Tesseract OCR (Required for Scanner)**:
  * **Windows**: Download the [UB-Mannheim installer](https://github.com/UB-Mannheim/tesseract/wiki). Ensure you check "Add to PATH" during install.
  * **Linux**: Run standard package manager to install `tesseract-ocr`
  * **macOS**: Use homebrew to install `tesseract`

### Step-by-Step Setup
1. **Clone the repository:**
   Run git clone on the repository URL and cd into the `openyugi` folder.
2. **Set up a Virtual Environment (Recommended):**
   Create a standard python virtual environment and activate it.
3. **Install Dependencies:**
   Run pip install against the `requirements.txt` file.
   *(Note: The scanner requires `opencv-python`, `torch`, and `easyocr`/`doctr`. Linux users may need additional system-level libraries for OpenCV).*
4. **Run the Application:**
   Start the application by running:
   `python main.py`
   The application server will start locally. Open your browser to `http://localhost:8080`.

---

## 📚 Documentation

Detailed guides, tutorials, and deep architectural dives can be found in our **[Docs / Wiki](docs/Home.md)**.
*The documentation covers everything from database schema structures and advanced UI modification, to detailed instructions on adding custom custom banlists and troubleshooting the neural network scanner.*

---

## 📸 Deep Dive: The AI Scanner

The OpenYuGi AI Webcam Scanner is one of its most powerful tools, utilizing a combination of advanced Computer Vision techniques to digitize your collection rapidly.

**How It Works:**
The pipeline operates using an event-driven state machine running on a background daemon to prevent UI freezing:
1. **Detection & Warp:** Detects the physical card boundary and applies a perspective warp to flatten it.
2. **Dual-Track OCR:** Simultaneously runs **EasyOCR** and **DocTR** on the flattened image to extract Set Codes, Passcodes, and Names.
3. **Computer Vision Extraction:** Analyzes visual metadata to detect Foil treatment (Rarity) and "1st Edition" text stamps.
4. **YOLO Art Matching:** Computes a feature vector using a YOLOv8 classification model and compares it against your local `data/images` database.
5. **Heuristic Resolution:** Scores candidates by Set Code (80 pts), Name (50 pts), and Art Style (40 pts) to predict the exact variant.

**Things to Be Aware Of (Best Practices):**
* **Lighting is Everything:** Glare on foil cards will break OCR and Art Matching. Ensure diffused, even lighting.
* **Ambiguity Handling:** When sets overlap (e.g., same Set Code, but both Ultra and Secret rares exist), the UI will prompt you to manually resolve the ambiguity before committing.
* **Background Contrast:** Use a dark, solid, non-reflective playmat. A busy background will confuse the edge-detection algorithm.
* **Hardware:** Running OCR and YOLO models simultaneously is demanding. While optimized for CPU, older hardware may experience slight latency per scan.

---

## 🗃️ Comprehensive List of Features

**Core Inventory System**
* Track infinite cards by unique combinations of Set Code, Rarity, Condition, Language, and Edition.
* Support for multiple separate JSON database files (e.g., "Main Collection", "Trade Binder", "Bulk").
* Pydantic-validated, plain-text local database structure (`data/collections/*.json`).
* Lightning-fast in-memory processing.

**User Interface (NiceGUI)**
* Dual View Modes: "Player Consolidated View" (Groups by base card) and "Collector View" (Groups by specific variant).
* Advanced filtering across Set Codes, Rarities, Stats (ATK/DEF, Scale, Level), and specific Storage Bins.
* Drag-and-Drop enabled interface using SortableJS for Bulk Adds and Storage moving.
* Lazy-loaded images with dedicated country flags for fast rendering of massive datasets.

**Deck Building & Gameplay**
* Build, edit, and manage decks using a visual interface.
* Live Banlist Validation for Advanced TCG, OCG, and Time-Wizard/Goat Formats.
* Direct integration with collection data: Instantly know exactly how many copies of a required card you physically own.
* Standard `.ydk` file export and import, making decks completely interoperable with EDOPro, YGOOmega, and other online simulators.

**Market Integration**
* Fetches daily prices and offers from Cardmarket and TCGPlayer.
* Real-time calculation of overall binder and deck values.

**Storage Management**
* Create unlimited customized Binders and Boxes.
* Visual Gallery representation of physical storage with live card counts.
* Atomic "Move" operations to transfer cards between locations safely.

**Data Portability & Modification**
* Native Cardmarket Stock File import (`.txt` and `.pdf`).
* Full Backup and Restore functionalities via OpenYuGi JSON formats.
* CSV Export functionality containing comprehensive card metadata and market prices.
* Built-in Database Editor: Fix wrong APIs, build custom proxy sets, or manually override card statistics and rarities locally.

**Scanner & Machine Vision**
* Live Webcam Art Recognition and OCR.
* Batch queuing system allowing you to scan 50 cards, review them, apply bulk edits (Condition/Lang), and commit simultaneously.
* Debug Lab for power users to tweak edge detection parameters, view cropped ROIs, and refine the perspective warp.

