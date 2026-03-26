from nicegui import ui
from src.ui.theme import apply_theme
from src.core.config import config_manager
from src.services.ygo_api import ygo_service
from src.services.sample_generator import generate_sample_collection

def create_layout(content_function):
    """
    Wraps the content_function in the standard application layout
    (Sidebar, Header, Content Area).
    """
    # Apply theme ensuring consistent colors
    apply_theme()

    def open_settings():
        with ui.dialog() as d, ui.card().classes('w-96'):
            ui.label('Settings').classes('text-h6')

            def change_lang(e):
                if e.value != config_manager.get_language():
                    config_manager.set_language(e.value)
                    ui.notify('Language changed. Please reload or navigate to refresh data.')
                    # Reloading simply via JS since ui.navigate.reload might not be available or reliable in all versions
                    ui.run_javascript('window.location.reload()')

            ui.select(['en', 'de', 'fr', 'it', 'pt'],
                      label='Language',
                      value=config_manager.get_language(),
                      on_change=change_lang).classes('w-full')

            def change_page_size(e):
                try:
                    val = int(e.value)
                    if val > 0:
                        config_manager.set_deck_builder_page_size(val)
                        ui.notify('Deck Builder page size saved.')
                except (ValueError, TypeError):
                    pass

            ui.number('Cards Per Page (Deck Builder)',
                      value=config_manager.get_deck_builder_page_size(),
                      min=1, max=100,
                      on_change=change_page_size).classes('w-full')

            def change_bulk_page_size(e):
                try:
                    val = int(e.value)
                    if val > 0:
                        config_manager.set_bulk_add_page_size(val)
                        ui.notify('Bulk Add page size saved.')
                except (ValueError, TypeError):
                    pass

            ui.number('Cards Per Page (Bulk Add)',
                      value=config_manager.get_bulk_add_page_size(),
                      min=1, max=100,
                      on_change=change_bulk_page_size).classes('w-full')

            ui.separator().classes('q-my-md')
            ui.label('Data Management').classes('text-subtitle2 text-grey')

            async def update_db():
                n = ui.notification('Updating Card Database...', type='info', spinner=True, timeout=None)
                try:
                    count = await ygo_service.fetch_card_database(config_manager.get_language())
                    n.dismiss()
                    ui.notify(f'Database updated. {count} cards loaded.', type='positive')
                except Exception as e:
                    n.dismiss()
                    ui.notify(f'Update failed: {e}', type='negative')

            with ui.button('Update Card Database', on_click=update_db, icon='cloud_download').classes('w-full').props('color=secondary'):
                ui.tooltip('Fetch the latest card data from the remote API')

            async def update_all_dbs():
                languages = ['en', 'de', 'fr', 'it', 'pt']
                for lang in languages:
                    n = ui.notification(f'Updating {lang}...', type='info', spinner=True, timeout=None)
                    try:
                        count = await ygo_service.fetch_card_database(lang)
                        n.dismiss()
                        ui.notify(f'Updated {lang}: {count} cards.', type='positive')
                    except Exception as e:
                        n.dismiss()
                        ui.notify(f'Failed to update {lang}: {e}', type='negative')

            with ui.button('Update All Languages DB', on_click=update_all_dbs, icon='cloud_sync').classes('w-full q-mt-sm').props('color=accent'):
                ui.tooltip('Fetch the latest card data for all supported languages')

            async def download_set_info_imgs():
                # Dialog for progress
                prog_dialog = ui.dialog().props('persistent')
                with prog_dialog, ui.card().classes('w-96'):
                    ui.label('Downloading Set Info & Images').classes('text-h6')
                    ui.label('Updating global set statistics and downloading pack art...').classes('text-sm text-grey')
                    p_bar = ui.linear_progress(0).classes('w-full q-my-md')
                    status_lbl = ui.label('Starting...')
                prog_dialog.open()

                def on_progress(val):
                    p_bar.value = val
                    status_lbl.set_text(f"{int(val * 100)}%")

                try:
                    await ygo_service.download_set_statistics_and_images(progress_callback=on_progress)
                    prog_dialog.close()
                    ui.notify(f'Set info and images downloaded.', type='positive')
                except Exception as e:
                    prog_dialog.close()
                    ui.notify(f"Error: {e}", type='negative')

            with ui.button('Download Set Info & Images', on_click=download_set_info_imgs, icon='photo_library').classes('w-full q-mt-sm').props('color=indigo'):
                ui.tooltip('Download metadata and images for all card sets')

            async def download_yugipedia_imgs():
                # Dialog for progress
                prog_dialog = ui.dialog().props('persistent')
                with prog_dialog, ui.card().classes('w-96'):
                    ui.label('Downloading Set Images (Yugipedia)').classes('text-h6')
                    ui.label('Searching and downloading high-quality set images...').classes('text-sm text-grey')
                    p_bar = ui.linear_progress(0).classes('w-full q-my-md')
                    status_lbl = ui.label('Starting...')
                prog_dialog.open()

                def on_progress(val):
                    p_bar.value = val
                    status_lbl.set_text(f"{int(val * 100)}%")

                try:
                    await ygo_service.download_set_images_from_yugipedia(progress_callback=on_progress)
                    prog_dialog.close()
                    ui.notify(f'Yugipedia set images downloaded.', type='positive')
                except Exception as e:
                    prog_dialog.close()
                    ui.notify(f"Error: {e}", type='negative')

            with ui.button('Download Set Images (Yugipedia)', on_click=download_yugipedia_imgs, icon='image').classes('w-full q-mt-sm').props('color=pink'):
                ui.tooltip('Replace set images with better ones from Yugipedia')

            async def download_all_imgs():
                # Dialog for progress
                prog_dialog = ui.dialog().props('persistent')
                with prog_dialog, ui.card().classes('w-96'):
                    ui.label('Downloading All Low Res Images').classes('text-h6')
                    ui.label('This may take a while...').classes('text-sm text-grey')
                    p_bar = ui.linear_progress(0).classes('w-full q-my-md')
                    status_lbl = ui.label('Starting...')
                prog_dialog.open()

                def on_progress(val):
                    p_bar.value = val
                    status_lbl.set_text(f"{int(val * 100)}%")

                try:
                    await ygo_service.download_all_images(progress_callback=on_progress, language=config_manager.get_language())
                    prog_dialog.close()
                    ui.notify(f'All low res images downloaded.', type='positive')
                except Exception as e:
                    prog_dialog.close()
                    ui.notify(f"Error: {e}", type='negative')

            with ui.button('Download All Low Res Images', on_click=download_all_imgs, icon='download_for_offline').classes('w-full q-mt-sm').props('color=secondary'):
                ui.tooltip('Download small images for all cards (saves bandwidth)')

            async def download_all_imgs_high():
                # Dialog for progress
                prog_dialog = ui.dialog().props('persistent')
                with prog_dialog, ui.card().classes('w-96'):
                    ui.label('Downloading All High Res Images').classes('text-h6')
                    ui.label('This may take a while and use significant disk space...').classes('text-sm text-grey')
                    p_bar = ui.linear_progress(0).classes('w-full q-my-md')
                    status_lbl = ui.label('Starting...')
                prog_dialog.open()

                def on_progress(val):
                    p_bar.value = val
                    status_lbl.set_text(f"{int(val * 100)}%")

                try:
                    await ygo_service.download_all_images_high_res(progress_callback=on_progress, language=config_manager.get_language())
                    prog_dialog.close()
                    ui.notify(f'All high res images downloaded.', type='positive')
                except Exception as e:
                    prog_dialog.close()
                    ui.notify(f"Error: {e}", type='negative')

            with ui.button('Download All High Res Images', on_click=download_all_imgs_high, icon='download_for_offline').classes('w-full q-mt-sm').props('color=purple'):
                ui.tooltip('Download high-quality images for all cards (requires disk space)')

            async def gen_sample_coll():
                n = ui.notification('Generating Sample Collection...', type='info', spinner=True, timeout=None)
                try:
                    filename = await generate_sample_collection()
                    n.dismiss()
                    ui.notify(f'Sample collection created: {filename}', type='positive')
                except Exception as e:
                    n.dismiss()
                    ui.notify(f"Generation failed: {e}", type='negative')

            with ui.button('Generate Sample Collection', on_click=gen_sample_coll, icon='playlist_add').classes('w-full q-mt-sm').props('color=positive'):
                 ui.tooltip('Create a random sample collection for testing')

            async def open_clean_db_dialog():
                from src.ui.import_tools import CardmarketParser # used just for some constants if needed, but maybe not
                from src.services.ygo_api import ygo_service
                from src.core.utils import is_set_code_compatible
                import copy

                with ui.dialog() as clean_d, ui.card().classes('w-full max-w-4xl'):
                    ui.label('Clean Database Entries').classes('text-h6')
                    ui.label('Remove database entries (variants) that do not match the selected language.').classes('text-sm text-grey')

                    lang_select = ui.select(['en', 'de', 'fr', 'it', 'pt'], label='Language to Scan', value='en').classes('w-full q-my-md')

                    preview_container = ui.column().classes('w-full q-mt-md')

                    state = {
                        'items_to_remove': [],
                        'original_db_snapshot': None,
                        'selected_lang': 'en'
                    }

                    def render_preview():
                        preview_container.clear()
                        with preview_container:
                            if not state['items_to_remove']:
                                ui.label('No incompatible entries found.').classes('text-positive')
                                return

                            ui.label(f"Found {len(state['items_to_remove'])} incompatible variants.").classes('text-warning font-bold q-mb-sm')

                            with ui.scroll_area().classes('h-64 w-full border border-gray-700 rounded p-2'):
                                with ui.grid(columns='auto 3fr 1fr 1fr').classes('w-full items-center gap-2 border-b border-gray-600 pb-2 font-bold text-grey-4'):
                                    ui.checkbox(value=True, on_change=lambda e: toggle_all(e.value)).classes('w-10 justify-center').props('dense')
                                    ui.label('Card Name')
                                    ui.label('Set Code')
                                    ui.label('Rarity')

                                # Render checkboxes manually (limit length or rely on scroll area for performance)
                                # For a lot of variants it might be slow, but typically it's < 1000
                                for item in state['items_to_remove']:
                                    with ui.grid(columns='auto 3fr 1fr 1fr').classes('w-full items-center gap-2 border-b border-gray-800 py-1'):
                                        # Use a fresh callback to prevent late binding issues
                                        def make_on_change(it):
                                            return lambda e: it.update({'include': e.value})
                                        ui.checkbox(value=item['include'], on_change=make_on_change(item)).classes('w-10 justify-center').props('dense')
                                        ui.label(item['card_name']).classes('truncate text-white')
                                        ui.label(item['set_code']).classes('font-mono text-yellow-500 text-sm')
                                        ui.label(item['rarity']).classes('text-sm text-grey-4')

                            with ui.row().classes('w-full justify-end gap-4 q-mt-md'):
                                ui.button('Cancel', on_click=clean_d.close).props('outline color=white')
                                ui.button('Remove Entries', on_click=apply_removal).props('color=negative')

                    def toggle_all(val):
                        for item in state['items_to_remove']:
                            item['include'] = val
                        render_preview()

                    async def scan_db():
                        lang = lang_select.value
                        state['selected_lang'] = lang
                        n = ui.notification(f'Scanning {lang} database...', type='info', spinner=True, timeout=None)
                        try:
                            cards = await ygo_service.load_card_database(lang)
                            # Deep copy snapshot for Undo
                            state['original_db_snapshot'] = [c.model_copy(deep=True) for c in cards] if cards and hasattr(cards[0], 'model_copy') else copy.deepcopy(cards)

                            items = []
                            for card in cards:
                                for variant in card.card_sets:
                                    if not is_set_code_compatible(variant.set_code, lang):
                                        items.append({
                                            'card_id': card.id,
                                            'variant_id': variant.variant_id,
                                            'card_name': card.name,
                                            'set_code': variant.set_code,
                                            'rarity': variant.set_rarity,
                                            'include': True,
                                            'variant_ref': variant,
                                            'card_ref': card
                                        })

                            state['items_to_remove'] = items
                            n.dismiss()
                            render_preview()
                        except Exception as e:
                            n.dismiss()
                            ui.notify(f'Scan failed: {e}', type='negative')

                    async def apply_removal():
                        lang = state['selected_lang']
                        cards = await ygo_service.load_card_database(lang)

                        to_remove = [it for it in state['items_to_remove'] if it['include']]
                        if not to_remove:
                            ui.notify('No entries selected for removal.', type='warning')
                            return

                        removed_count = 0

                        # Map cards by ID for quick modification
                        card_map = {c.id: c for c in cards}
                        cards_to_delete = set()

                        for item in to_remove:
                            card = card_map.get(item['card_id'])
                            if card:
                                original_len = len(card.card_sets)
                                card.card_sets = [v for v in card.card_sets if v.variant_id != item['variant_id']]
                                if len(card.card_sets) < original_len:
                                    removed_count += 1

                                if len(card.card_sets) == 0:
                                    cards_to_delete.add(card.id)

                        # Remove cards that have 0 variants left
                        if cards_to_delete:
                            cards[:] = [c for c in cards if c.id not in cards_to_delete]

                        # Save
                        await ygo_service.save_card_database(cards, lang)

                        ui.notify(f'Successfully removed {removed_count} database entries.', type='positive')
                        clean_d.close()

                        # Save state for undo
                        undo_state['snapshot'] = state['original_db_snapshot']
                        undo_state['lang'] = lang

                        # Show Undo button globally or in settings
                        undo_btn.visible = True
                        undo_btn.update()

                    with ui.row().classes('w-full justify-between items-center'):
                        ui.button('Scan', on_click=scan_db).props('color=primary')
                        ui.button('Cancel', on_click=clean_d.close).props('flat')

                clean_d.open()

            with ui.button('Clean Database Entries', on_click=open_clean_db_dialog, icon='cleaning_services').classes('w-full q-mt-sm').props('color=warning text-color=dark'):
                 ui.tooltip('Remove database entries that do not match the database language')

            # To handle undo we store the state in a closure or global. Let's use a mutable object attached to the function.
            undo_state = {'snapshot': None, 'lang': None}

            async def undo_clean():
                if undo_state['snapshot'] and undo_state['lang']:
                    try:
                        lang = undo_state['lang']
                        # ygo_service.save_card_database overrides the current loaded cards with the list provided
                        await ygo_service.save_card_database(undo_state['snapshot'], lang)

                        # Invalidate internal cache since objects were replaced
                        # The cache in ygo_service keeps a reference to the old list.
                        # ygo_service.save_card_database handles this properly.

                        ui.notify(f'Successfully restored the {lang} database to its previous state.', type='positive')

                        # Hide undo button
                        undo_state['snapshot'] = None
                        undo_state['lang'] = None
                        undo_btn.visible = False
                        undo_btn.update()
                    except Exception as e:
                        ui.notify(f'Failed to restore database: {e}', type='negative')

            with ui.row().classes('w-full justify-end q-mt-md'):
                undo_btn = ui.button('Undo Clean', icon='undo', on_click=undo_clean).props('flat color=warning')
                undo_btn.visible = False
                with ui.button('Close', on_click=d.close).props('flat'):
                    ui.tooltip('Close settings')
        d.open()

    # Define the drawer first so it's available for the toggle button
    with ui.left_drawer(value=True).classes('bg-dark text-white') as left_drawer:
        with ui.column().classes('w-full q-mt-md'):
            ui.label('Navigation').classes('text-grey-4 q-px-md text-sm uppercase font-bold')

            def nav_button(text, icon, target):
                ui.button(text, icon=icon, on_click=lambda: ui.navigate.to(target)).props('flat align=left').classes('w-full text-grey-3 hover:bg-white/10')

            nav_button('Dashboard', 'dashboard', '/')
            nav_button('Collection', 'style', '/collection')
            nav_button('Storage', 'inventory_2', '/storage')
            nav_button('Browse Sets', 'library_books', '/sets')
            nav_button('Deck Builder', 'construction', '/decks')
            nav_button('Bulk Add', 'playlist_add', '/bulk_add')
            nav_button('Scan Cards', 'camera', '/scan')
            nav_button('Import Tools', 'qr_code_scanner', '/import')
            nav_button('Edit Card DB', 'edit', '/db_editor')

            ui.separator().classes('q-my-md bg-grey-8')
            ui.label('Settings').classes('text-grey-4 q-px-md text-sm uppercase font-bold')

            # Custom button for Configuration
            with ui.button('Configuration', icon='settings', on_click=open_settings).props('flat align=left').classes('w-full text-grey-3 hover:bg-white/10'):
                ui.tooltip('Open application settings and database management')

    with ui.header().classes(replace='row items-center') as header:
        header.classes('bg-primary text-white')
        # Now left_drawer is definitely defined in scope
        with ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white'):
            pass
        ui.label('OpenYuGi').classes('text-h6 q-ml-md font-bold')

    with ui.column().classes('w-full q-pa-md items-start'):
        content_function()
