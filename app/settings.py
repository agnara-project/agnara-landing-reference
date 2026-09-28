import os
from typing import Final


class Settings:
    # Environment
    ENV: Final[str] = os.getenv("APP_ENV", "production")
    DEBUG: Final[bool] = ENV == "development"

    # HTTP
    HOST: Final[str] = os.getenv("HOST", "0.0.0.0")
    PORT: Final[int] = int(os.getenv("PORT", "8000"))

    # Database
    DATABASE_URL: Final[str] = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:////data/agnara.db"
    )

    # Security
    SESSION_SECRET: Final[str] = os.getenv("SESSION_SECRET")
    SECURE_COOKIES: Final[bool] = os.getenv("SECURE_COOKIES", "true").lower() == "true"

    # Admin
    ADMIN_USERNAME: Final[str] = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH: Final[str] = os.getenv("ADMIN_PASSWORD_HASH")

    def __init__(self):
        if self.ENV == "production":
            if (
                not self.SESSION_SECRET
                or self.SESSION_SECRET == "fallback-dev-secret-key-change-me"
            ):
                raise ValueError("SESSION_SECRET must be set securely in production.")
            if not self.ADMIN_PASSWORD_HASH:
                raise ValueError("ADMIN_PASSWORD_HASH must be set in production.")
        else:
            # Fallbacks for dev if not set
            if not self.SESSION_SECRET:
                self.SESSION_SECRET = "fallback-dev-secret-key-change-me"


settings = Settings()
