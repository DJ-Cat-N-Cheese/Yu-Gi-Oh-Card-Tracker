# OpenYuGi - Yugioh Card Collection Manager

A local Yugioh card collection manager built with Python and NiceGUI.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    ```bash
    PYTHONPATH=. python main.py
    ```
    Open your browser at `http://localhost:8080`.

## Architecture

The project follows a modular architecture:

*   **`src/core`**: Domain models and persistence logic. Data is stored in JSON files in the `data/` directory.
*   **`src/services`**: Logic for external API integration (YGOPRODeck) and local file management (images).
*   **`src/ui`**: Frontend components built with [NiceGUI](https://nicegui.io/).

## API & Data

Card data is fetched from the [YGOPRODeck API](https://db.ygoprodeck.com/api/v7/cardinfo.php).
The application caches the card database locally in `data/db/card_db.json`. This database is updated manually via the Settings menu.

## Image Storage

Card images are stored locally in the `data/images/` directory to reduce load on the external API and provide faster subsequent access.

### Lazy Loading
By default, the application uses a "lazy loading" strategy. When you navigate to a page in your collection, the application checks if the required images exist locally. If not, it downloads them immediately. This ensures you only download images for cards you actually view.

### Bulk Download
If you prefer to have all images available immediately (to avoid loading delays), you can go to **Settings > Download All Images**. This will download the artwork for every card in the database.

## Troubleshooting

*   **Missing Images:** If images fail to load, check your internet connection and try reloading the page. The application will attempt to redownload missing images.
*   **Database Updates:** If new cards are released, use the "Update Card Database" button in Settings to refresh your local cache.
