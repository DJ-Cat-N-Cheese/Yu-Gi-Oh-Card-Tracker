"""Single-user authentication and session security helpers."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import stat
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

from src.core.config import ConfigManager, config_manager


AUTH_SESSION_KEY = "authenticated"
AUTH_REVISION_KEY = "auth_revision"
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 128
MAX_USERNAME_LENGTH = 64
STORAGE_SECRET_PATH = Path("data/.storage_secret")


class AuthService:
    """Validate and update the one configured OpenYuGi account."""

    def __init__(self, manager: ConfigManager = config_manager) -> None:
        self.config_manager = manager

    @staticmethod
    def validate_username(username: str) -> str:
        normalized = username.strip() if isinstance(username, str) else ""
        if not normalized:
            raise ValueError("Username is required.")
        if len(normalized) > MAX_USERNAME_LENGTH:
            raise ValueError(f"Username must be {MAX_USERNAME_LENGTH} characters or fewer.")
        if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
            raise ValueError("Username cannot contain control characters.")
        return normalized

    @staticmethod
    def validate_password(password: str) -> None:
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if len(password) > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Password must be {MAX_PASSWORD_LENGTH} characters or fewer.")

    def authenticate(self, username: str, password: str) -> bool:
        stored_username = self.config_manager.get_auth_username()
        username_matches = hmac.compare_digest(
            (username.strip() if isinstance(username, str) else "").encode("utf-8"),
            stored_username.encode("utf-8"),
        )
        try:
            password_matches = check_password_hash(
                self.config_manager.get_auth_password_hash(),
                password if isinstance(password, str) else "",
            )
        except (TypeError, ValueError):
            password_matches = False
        return username_matches and password_matches

    def update_credentials(
        self,
        current_password: str,
        new_username: str,
        new_password: str = "",
        confirm_password: str = "",
    ) -> None:
        if not self.authenticate(self.config_manager.get_auth_username(), current_password):
            raise ValueError("Current password is incorrect.")

        username = self.validate_username(new_username)
        password_hash = self.config_manager.get_auth_password_hash()
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise ValueError("New passwords do not match.")
            self.validate_password(new_password)
            password_hash = generate_password_hash(new_password, method="scrypt")

        self.config_manager.set_auth_credentials(username, password_hash)

    def revision(self) -> str:
        """Identify the active credentials so changes invalidate older sessions."""
        payload = f"{self.config_manager.get_auth_username()}\0{self.config_manager.get_auth_password_hash()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_storage_secret(
    secret_path: Path = STORAGE_SECRET_PATH,
    environ: dict[str, str] | None = None,
) -> str:
    """Load a stable session signing secret, generating a local one if needed."""
    environment = os.environ if environ is None else environ
    configured_secret = environment.get("OPENYUGI_STORAGE_SECRET", "")
    if configured_secret:
        if len(configured_secret) < 32:
            raise ValueError("OPENYUGI_STORAGE_SECRET must be at least 32 characters.")
        return configured_secret

    secret_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        secret = secret_path.read_text(encoding="utf-8").strip()
        if len(secret) < 32:
            raise ValueError(f"Session secret in {secret_path} is invalid.")
        try:
            os.chmod(secret_path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
        return secret

    secret = secrets.token_urlsafe(48)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        file.write(secret)
    return secret


# SECURITY: Passwords use Werkzeug's memory-hard, salted scrypt hashes. The hash
# and session signing secret still live in local files. Deployments should use
# HTTPS, restrict those files to the service account, and inject a strong
# OPENYUGI_STORAGE_SECRET via the environment (or a secrets manager).
auth_service = AuthService()
