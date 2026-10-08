from . import db
from datetime import datetime


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=True)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to issues
    issues = db.relationship('Issue', backref='book', lazy=True)

    def is_available(self):
        return self.available_copies > 0

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
