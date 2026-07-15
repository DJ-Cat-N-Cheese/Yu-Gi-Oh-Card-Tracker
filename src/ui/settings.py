from nicegui import app, run, ui

from src.core.config import config_manager
from src.services.auth_service import AUTH_REVISION_KEY, auth_service
from src.services.sample_generator import generate_sample_collection
from src.services.ygo_api import ygo_service


def settings_page() -> None:
    """Render application preferences, account security, and data tools."""
    ui.label('Settings').classes('text-h4 text-weight-bold')
    ui.label('Manage application preferences, credentials, and local card data.').classes(
        'text-subtitle1 text-grey-5 q-mb-md'
    )

    with ui.grid(columns=1).classes('w-full gap-4 lg:grid-cols-2'):
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Application').classes('text-h6')
            ui.label('Display language and page sizes').classes('text-caption text-grey-5 q-mb-md')
            language = ui.select(
                ['en', 'de', 'fr', 'it', 'pt'],
                label='Language',
                value=config_manager.get_language(),
            ).props('outlined').classes('w-full')
            deck_page_size = ui.number(
                'Cards Per Page (Deck Builder)',
                value=config_manager.get_deck_builder_page_size(),
                min=1,
                max=100,
            ).props('outlined').classes('w-full')
            bulk_page_size = ui.number(
                'Cards Per Page (Bulk Add)',
                value=config_manager.get_bulk_add_page_size(),
                min=1,
                max=100,
            ).props('outlined').classes('w-full')

            async def save_application_settings() -> None:
                try:
                    deck_size = int(deck_page_size.value)
                    bulk_size = int(bulk_page_size.value)
                    if not 1 <= deck_size <= 100 or not 1 <= bulk_size <= 100:
                        raise ValueError('Page sizes must be between 1 and 100.')

                    await run.io_bound(
                        config_manager.set_application_settings,
                        language.value,
                        deck_size,
                        bulk_size,
                    )
                    ui.notify('Application settings saved.', type='positive')
                except (TypeError, ValueError) as error:
                    ui.notify(str(error), type='negative')

            ui.button(
                'Save application settings',
                icon='save',
                on_click=save_application_settings,
            ).props('color=secondary').classes('w-full q-mt-md')

        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Account security').classes('text-h6')
            ui.label('Changing either credential requires your current password.').classes(
                'text-caption text-grey-5 q-mb-md'
            )
            account_username = ui.input(
                'Username', value=config_manager.get_auth_username()
            ).props('outlined autocomplete=username maxlength=64').classes('w-full')
            current_password = ui.input(
                'Current password', password=True, password_toggle_button=True
            ).props('outlined autocomplete=current-password').classes('w-full')
            new_password = ui.input(
                'New password', password=True, password_toggle_button=True
            ).props('outlined autocomplete=new-password hint="Leave blank to keep current password"').classes('w-full')
            confirm_password = ui.input(
                'Confirm new password', password=True, password_toggle_button=True
            ).props('outlined autocomplete=new-password').classes('w-full')

            async def save_credentials() -> None:
                try:
                    await run.io_bound(
                        auth_service.update_credentials,
                        current_password.value,
                        account_username.value,
                        new_password.value,
                        confirm_password.value,
                    )
                except ValueError as error:
                    ui.notify(str(error), type='negative')
                    return

                app.storage.user[AUTH_REVISION_KEY] = auth_service.revision()
                current_password.set_value('')
                new_password.set_value('')
                confirm_password.set_value('')
                account_username.set_value(config_manager.get_auth_username())
                ui.notify('Credentials updated. Other sessions have been signed out.', type='positive')

            ui.button('Save credentials', icon='lock', on_click=save_credentials).props(
                'color=secondary'
            ).classes('w-full q-mt-md')

    with ui.card().classes('w-full q-pa-lg q-mt-md'):
        ui.label('Data management').classes('text-h6')
        ui.label('Refresh card metadata and cached imagery. Large downloads can take a while.').classes(
            'text-caption text-grey-5 q-mb-md'
        )

        async def run_action(message, action, success_message):
            notification = ui.notification(message, type='info', spinner=True, timeout=None)
            try:
                result = await action()
                notification.dismiss()
                ui.notify(success_message(result), type='positive')
            except Exception as error:  # external service errors are surfaced to the user
                notification.dismiss()
                ui.notify(f'Operation failed: {error}', type='negative')

        async def update_db():
            await run_action(
                'Updating card database...',
                lambda: ygo_service.fetch_card_database(config_manager.get_language()),
                lambda count: f'Database updated. {count} cards loaded.',
            )

        async def update_all_dbs():
            async def update():
                total = 0
                for language_code in ['en', 'de', 'fr', 'it', 'pt']:
                    total += await ygo_service.fetch_card_database(language_code)
                return total

            await run_action(
                'Updating all language databases...', update, lambda count: f'All databases updated ({count} cards).'
            )

        async def download_set_info():
            await run_action(
                'Downloading set information and images...',
                ygo_service.download_set_statistics_and_images,
                lambda _: 'Set information and images downloaded.',
            )

        async def download_yugipedia_images():
            await run_action(
                'Downloading set images from Yugipedia...',
                ygo_service.download_set_images_from_yugipedia,
                lambda _: 'Yugipedia set images downloaded.',
            )

        async def download_low_resolution_images():
            await run_action(
                'Downloading all low resolution images...',
                lambda: ygo_service.download_all_images(language=config_manager.get_language()),
                lambda _: 'All low resolution images downloaded.',
            )

        async def download_high_resolution_images():
            await run_action(
                'Downloading all high resolution images...',
                lambda: ygo_service.download_all_images_high_res(language=config_manager.get_language()),
                lambda _: 'All high resolution images downloaded.',
            )

        async def generate_sample():
            await run_action(
                'Generating sample collection...',
                generate_sample_collection,
                lambda filename: f'Sample collection created: {filename}',
            )

        with ui.grid(columns=1).classes('w-full gap-3 sm:grid-cols-2 lg:grid-cols-3'):
            ui.button('Update card database', icon='cloud_download', on_click=update_db).classes('w-full')
            ui.button('Update all languages', icon='cloud_sync', on_click=update_all_dbs).classes('w-full')
            ui.button('Download set info & images', icon='photo_library', on_click=download_set_info).classes('w-full')
            ui.button('Download Yugipedia set images', icon='image', on_click=download_yugipedia_images).classes('w-full')
            ui.button('Download low-res card images', icon='download', on_click=download_low_resolution_images).classes('w-full')
            ui.button('Download high-res card images', icon='high_quality', on_click=download_high_resolution_images).classes('w-full')
            ui.button('Generate sample collection', icon='playlist_add', on_click=generate_sample).props(
                'color=positive'
            ).classes('w-full')
