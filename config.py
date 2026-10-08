import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = os.environ.get("DATABASE_URL")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


class Config:

    # Security
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    # Database
    if DATABASE_URL:
        # Some PostgreSQL providers may return postgres://
        # SQLAlchemy expects postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # SQLite for local development
        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///"
            + os.path.join(BASE_DIR, "database", "library.db")
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Library settings
    FINE_PER_DAY = 5
    MAX_BORROW_DAYS = 14

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Only enable secure cookies in production
    SESSION_COOKIE_SECURE = (
        ENVIRONMENT == "production"
    )