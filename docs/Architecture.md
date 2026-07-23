# Architecture & Data Model

This guide is the technical deep dive for OpenYuGi: how the application is put together, the rules that keep it consistent, how a collection change flows from click to disk, and how a user's collection is actually modeled on disk.

If you are changing implementation code, read [`AGENTS.md`](../AGENTS.md) as well — it is the authoritative architectural manual for contributors and coding assistants.

## Technology stack

OpenYuGi is a server-rendered Python application built with **NiceGUI**, **FastAPI**, **Pydantic**, and local filesystem persistence. There is no SQL or NoSQL database; persistent state lives in ordinary files beneath `data/` (see [Local data, backups, and offline use](../README.md#-local-data-backups-and-offline-use) in the README).

## Repository layout

| Directory | Responsibility |
| --- | --- |
| `src/core/` | Domain models, configuration, persistence, constants, and changelogs; no UI code |
| `src/services/` | Collection mutation, APIs, authentication, pricing, images, imports, storage, and other integrations |
| `src/services/scanner/` | Computer-vision models, pipeline, worker manager, and scan events |
| `src/ui/` | NiceGUI pages, layout, theme, and page controllers |
| `src/ui/components/` | Reusable card, filter, structure-deck, and ambiguity components |
| `src/api/` | Authenticated FastAPI request models and `/api/v1` routes |
| `tests/` | Automated test suite |
| `docs/` | Feature guides and screenshots |
| `data/` | Runtime user data and caches; ignored by Git |

## Important implementation rules

1. **Use `CollectionEditor` for card inventory mutations.** It creates and removes parent nodes, merges equivalent entries, generates variant IDs, and performs storage transfers consistently. UI code must not mutate `Collection.cards` directly.
2. **Keep the UI event loop non-blocking.** Filesystem operations, network calls, and heavy computation must run through `await run.io_bound(...)`, an asynchronous client, or a dedicated worker thread.
3. **Deep-copy mutable Pydantic state for snapshots.** Use `model.model_copy(deep=True)` when an undo snapshot or isolated working copy is needed.
4. **Preserve card identity semantics.** Alternate-art IDs need to resolve to their base ID for gameplay ownership and banlist calculations while remaining distinct for collector inventory.
5. **Keep API metadata transient.** A collection stores ownership state, not a duplicate of the full `ApiCard` database.
6. **Update NiceGUI only from its UI context.** Background scanner threads emit queued events; they do not call `ui.notify` or mutate components directly.

## Collection transaction flow

```text
UI or API request
    ↓
Load Collection Pydantic model
    ↓
CollectionEditor.apply_change(...) / move_card(...)
    ↓
Record supported changelog operation
    ↓
PersistenceManager saves a full replacement file
    ↓
Refresh the affected UI state
```

## Drag and drop

Bulk Add and Storage use SortableJS in the browser. A frontend `onAdd` handler dispatches a `card_drop` event containing the card and source/target identifiers. The Python handler validates the event, performs the backend mutation, saves the collection, and refreshes the rendered content.

## Authenticated API

The application includes authenticated `/api/v1` endpoints for collection listing and mutation, card and set reference data, imports, and changelog access. The browser session authentication also protects these routes; unauthenticated API requests receive HTTP 401. Inspect `src/api/routes.py` and its Pydantic request models before integrating an external client.

## Scanner threading model

The `ScannerManager` performs processing on a dedicated worker thread. It places requests on a queue and emits lifecycle events; the NiceGUI page consumes those events with a timer instead of updating UI objects directly from the worker thread. This is the concrete application of implementation rule 6, and it is why the scanner never blocks the UI event loop even while running heavy computer-vision models.

For the full scanner pipeline, matching algorithm, and Debug Lab reference, see [Card Scanning](CardScanning.md).

## Collection data model

The collection hierarchy separates card identity, printing identity, and physical copies:

```text
Collection
└── CollectionCard                 base card identity (`card_id`)
    └── CollectionVariant          set + rarity + artwork (`variant_id`)
        └── CollectionEntry        condition + language + edition + location
```

- `CollectionCard` groups an abstract card identity by API card ID.
- `CollectionVariant` identifies a printing. Its deterministic ID incorporates card ID, set code, rarity, and image ID so alternate artwork remains distinct.
- `CollectionEntry` represents a physical stack. Entries with the same condition, language, first-edition flag, and storage location share one quantity.
- `ApiCard` reference objects come from the local API cache and are joined at runtime. They are not serialized into a user's collection.

A shortened collection file looks like this:

```json
{
  "name": "Main Collection",
  "description": "Personal cards",
  "storage_definitions": [
    {
      "name": "Binder 1",
      "type": "Binder",
      "description": "Main trade binder"
    }
  ],
  "cards": [
    {
      "card_id": 46986414,
      "name": "Dark Magician",
      "variants": [
        {
          "variant_id": "deterministically-generated-id",
          "set_code": "LOB-EN005",
          "rarity": "Ultra Rare",
          "image_id": 46986414,
          "entries": [
            {
              "condition": "Near Mint",
              "language": "EN",
              "first_edition": true,
              "quantity": 2,
              "storage_location": "Binder 1",
              "purchase_price": 0.0,
              "market_value": 0.0,
              "purchase_date": null
            }
          ]
        }
      ]
    }
  ]
}
```

Collection files are loaded into Pydantic models and saved by replacing the full file through the persistence layer. Do not edit a collection while OpenYuGi is running; the next application save may overwrite the external change.
