import sys
import os

# Mock dependencies to allow import
sys.modules['nicegui'] = type('Mock', (object,), {'ui': type('MockUI', (object,), {'refreshable': lambda f: f, 'page': lambda f: f}), 'run': type('MockRun', (object,), {'io_bound': lambda *a, **k: None})})()
sys.modules['src.core.persistence'] = type('Mock', (object,), {'persistence': type('MockP', (object,), {'list_collections': lambda: [], 'load_ui_state': lambda: {}})()})()
sys.modules['src.core.changelog_manager'] = type('Mock', (object,), {'changelog_manager': type('MockC', (object,), {})()})()
sys.modules['src.core.config'] = type('Mock', (object,), {'config_manager': type('MockCm', (object,), {'get_language': lambda: 'en', 'get_bulk_add_page_size': lambda: 50})()})()
sys.modules['src.services.ygo_api'] = type('Mock', (object,), {'ygo_service': type('MockY', (object,), {})(), 'ApiCard': type('MockAC', (object,), {})()})()
sys.modules['src.services.image_manager'] = type('Mock', (object,), {'image_manager': type('MockIM', (object,), {})()})()
sys.modules['src.services.collection_editor'] = type('Mock', (object,), {'CollectionEditor': type('MockCE', (object,), {})()})()
sys.modules['src.ui.components.filter_pane'] = type('Mock', (object,), {'FilterPane': type('MockFP', (object,), {})})()
sys.modules['src.ui.components.single_card_view'] = type('Mock', (object,), {'SingleCardView': type('MockSCV', (object,), {})})()
sys.modules['src.ui.components.structure_deck_dialog'] = type('Mock', (object,), {'StructureDeckDialog': type('MockSDD', (object,), {})})()

# Import
try:
    from src.ui.bulk_add import BulkAddPage
    print("Import successful")

    if hasattr(BulkAddPage, 'apply_library_filters'):
        print("apply_library_filters exists")
    else:
        print("ERROR: apply_library_filters MISSING")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
