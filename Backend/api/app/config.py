import os


DEV_JWT_SECRET = "dev_secret_change_me"
DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
MIN_JWT_SECRET_LENGTH = 32


def app_env() -> str:
    return os.getenv("APP_ENV", "development").strip().lower()


def cors_origins() -> list[str]:
    return [o.strip() for o in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",") if o.strip()]


def admin_emails() -> set[str]:
    return {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}


def validate_secrets() -> None:
    """Refuse to start outside development with a missing, default, or short JWT secret."""
    if app_env() == "development":
        return
    secret = os.getenv("JWT_SECRET", "")
    if secret == DEV_JWT_SECRET or len(secret) < MIN_JWT_SECRET_LENGTH:
        raise RuntimeError(
            f"Set JWT_SECRET to a random value of at least {MIN_JWT_SECRET_LENGTH} characters "
            f"when APP_ENV is '{app_env()}'"
        )
