import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = os.environ.get("DATABASE_URL")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    if DATABASE_URL:

        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )

        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:

        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///"
            + os.path.join(BASE_DIR, "database", "library.db")
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FINE_PER_DAY = 5
    MAX_BORROW_DAYS = 14

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (ENVIRONMENT == "production")