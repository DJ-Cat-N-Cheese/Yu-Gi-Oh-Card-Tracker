# Settings

OpenYuGi requires a login before any collection, API, image, debug, or settings route is available. On first run, sign in with username `admin` and password `admin`, then change the default credentials from the dedicated **Settings** page in the sidebar.

## Account Security

- **Username**: Change the single local account name (maximum 64 characters).
- **Current password**: Required before either credential can be changed.
- **New password / confirmation**: Passwords must match and contain at least 4 characters. Leave both blank to keep the current password.
- **Log out**: Ends the current authenticated session. Changing credentials also invalidates other existing sessions.

Passwords are stored as salted scrypt hashes, never plaintext. The credential hash and generated session secret are local files, so deployments should use HTTPS and restrict filesystem access to the OpenYuGi service account. Production deployments should inject a strong `OPENYUGI_STORAGE_SECRET` environment variable and set `OPENYUGI_SECURE_COOKIES=true` when served over HTTPS.

## Application

- **Language**: Change the card database language (English, German, French, Italian, Portuguese).
  - *Note*: Changing language requires a database update to fetch localized names.
- **Page Size**: Adjust how many cards appear per page in Deck Builder and Bulk Add.

## Data Management

- **Update Card Database**: Fetches the latest card definitions from the online API (Yu-Gi-Oh! API).
- **Update All Languages**: Updates databases for all supported languages in one go.
- **Download Images**:
  - **Low Res**: Essential for the Collection view and Scanner matching. Recommended to run this once.
  - **High Res**: Downloads high-quality artwork. Warning: Uses significant disk space.
- **Generate Sample Collection**: Creates a dummy collection with random cards for testing purposes.
