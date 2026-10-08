import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'database', 'library.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Fine overdue calculation (rupees per day)
    FINE_PER_DAY = 5
    # Maximum borrow duration in days
    MAX_BORROW_DAYS = 14
