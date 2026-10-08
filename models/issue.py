from . import db
from datetime import datetime, timedelta
from flask import current_app


class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    # status values:
    #   'issued'         – book is with the member
    #   'pending_return' – member requested return, awaiting admin confirmation
    #   'returned'       – admin confirmed the physical return
    status = db.Column(db.String(20), nullable=False, default='issued')

    fine = db.Column(db.Float, default=0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.due_date:
            max_days = current_app.config.get('MAX_BORROW_DAYS', 14)
            self.due_date = datetime.utcnow() + timedelta(days=max_days)

    def calculate_fine(self):
        """Calculate overdue fine based on return_date (or now if not yet returned)."""
        check_date = self.return_date if self.return_date else datetime.utcnow()
        overdue_days = (check_date - self.due_date).days
        if overdue_days > 0:
            fine_per_day = current_app.config.get('FINE_PER_DAY', 5)
            return overdue_days * fine_per_day
        return 0.0

    def is_overdue(self):
        """True only when the book is still out (issued/pending) and past due date."""
        if self.status == 'returned':
            return False
        return datetime.utcnow() > self.due_date

    def is_pending_return(self):
        return self.status == 'pending_return'

    def __repr__(self):
        return f'<Issue user={self.user_id} book={self.book_id} status={self.status}>'
