# 🃏 OpenYuGi

> **The Ultimate Local-First Yugioh Collection Manager**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![NiceGUI](https://img.shields.io/badge/Built_with-NiceGUI-red.svg)](https://nicegui.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**OpenYuGi** is a professional-grade, privacy-focused application designed for serious collectors and players. Unlike cloud-based alternatives, OpenYuGi runs entirely on your local machine, giving you absolute ownership of your data while providing advanced features like comprehensive deck building, granular rarity tracking, and market data integration.

---

## 🚀 Getting Started

Follow this guide to get your first collection up and running in minutes.

### 1. Installation

**Prerequisites**
*   **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
*   **(Optional) Tesseract OCR**: Only required if you intend to use the experimental scanner feature.
    *   *Windows*: [Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH)
    *   *Linux*: `sudo apt-get install tesseract-ocr`

**Setup**
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/openyugi.git
cd openyugi

# 2. Create a Virtual Environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt
```

**Run the App**
```bash
python main.py
```
Open your browser at `http://localhost:8080`.

### 2. Creating Your First Collection
1.  Navigate to the **Collection** page using the sidebar or quick nav.
2.  In the top-left dropdown menu (labeled "Collection"), select **+ New Collection**.
3.  Enter a name (e.g., "Main Binder") and click **Create**.

### 3. Adding Cards
There are three ways to populate your collection:
*   **Manual Search**: In the **Collection** view, ensure the "Owned" toggle is **OFF**. Search for any card (e.g., "Dark Magician"). Click the card image to open the detail view, then add the specific quantity, set, and rarity you own.
*   **Bulk Add**: Go to the **Bulk Add** page. Paste a list of card names (one per line) to add them all at once.
*   **Import**: If you have a backup or a Cardmarket export, use the **Import Tools** page to migrate your data.

---

## ✨ Features Guide

### 📦 Smart Collection Management
OpenYuGi offers a powerful interface to manage inventories of any size.

*   **Dual View Modes**:
    *   **Consolidated View**: Best for players. Groups all printings of a card together, showing you your total playable copies regardless of rarity.
    *   **Collectors View**: Best for traders and collectors. Lists every specific printing (Set Code + Rarity + Edition) as a separate row, allowing you to track exactly which version you own (e.g., *LOB-EN001 Ultra Rare vs. LOB-EN001 Unlimited*).
*   **Advanced Filtering**: Drill down into your collection with precision. Filter by **Set Code**, **Rarity**, **Price Range**, **Quantity**, or Card Stats (ATK/DEF/Level).
*   **Market Data**: Automatically fetches price data (Cardmarket/TCGPlayer) to give you an estimated value of your collection.
*   **Undo System**: Made a mistake? The global Undo button allows you to revert your last action instantly.

### 🛠 Professional Deck Builder
A dedicated environment for theory-crafting and tournament prep.

*   **Format Support**: Create, edit, and save decks in the standard `.ydk` format, fully compatible with simulators like EDOPro and YGOOmega.
*   **Collection Integration**: The builder highlights cards you own, helping you distinguish between decks you can build IRL and those you need to buy singles for.
*   **Banlist Validation**: Integrated checks against **TCG**, **OCG**, and **Goat** banlists.
*   **Drag & Drop**: Intuitive interface for moving cards between Main, Extra, and Side decks.

### 🧩 Additional Tools

**Import / Export**
*   **Cardmarket Import**: Upload a Cardmarket stock export file (`.txt` or `.pdf`) to instantly populate your collection.
*   **JSON Backups**: Full export of your data to JSON format for safekeeping or migration.
*   **CSV Export**: Export your collection list to CSV for use in spreadsheets.

**Database Editor**
*   **Custom Cards**: Add local-only cards or proxies to your database.
*   **Errata & Fixes**: Locally correct card stats or text without waiting for an upstream API update.

**Advanced Banlists**
*   **Historical Formats**: Includes built-in support for Goat Format.
*   **Auto-Update**: Fetches the latest lists directly from the web.

### 📸 AI-Powered Webcam Scanner (Experimental)
![Status](https://img.shields.io/badge/Status-Not%20Working%20Yet-red)

*Note: This feature is currently a work in progress and is not yet functional for daily use.*

The goal of this feature is to allow real-time card recognition via webcam using OpenCV and Tesseract OCR.
- **Planned**: Auto-detection of set codes.
- **Planned**: Hands-free rapid entry.

---

## ⚠️ Troubleshooting & "Watch Out For"

### 1. "The Scanner button is grayed out"
**Cause:** The application failed to load `opencv` or `pytesseract`.
**Fix:** This is normal if you haven't installed the optional Tesseract software. The rest of the app works fine without it.

### 2. "Images aren't loading"
**Behavior:** OpenYuGi uses a **Lazy Loading** strategy. It only downloads images when you first view them to save bandwidth and disk space.
**Fix:** Ensure you have an active internet connection for the first load.

### 3. "My changes aren't saving"
**Note:** The application disables "Hot Reload" (`reload=False` in `main.py`) because it writes to the `data/` directory. If you are developing and editing code, you must manually restart the server to see code changes.

---

## ❓ FAQ

**Q: Where is my data stored?**
A: Everything is in the `data/` folder in the project root. You can back up this folder to save your entire state.

**Q: Can I use Edison Format?**
A: Currently, the app defaults to TCG, OCG, and Goat banlists. Edison is not yet explicitly supported in the auto-fetcher.

**Q: Is this legal?**
A: OpenYuGi is a fan-made project. Card images and data are provided by the YGOPRODeck API. This tool is for personal collection management only.

---

*Built with ❤️ by the OpenYuGi Community.*
