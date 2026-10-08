from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .book import Book
from .issue import Issue
