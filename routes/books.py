from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.book import Book
from models.issue import Issue
from functools import wraps

books_bp = Blueprint('books', __name__)


def admin_required(f):
    """Decorator: restricts route to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('books.dashboard'))
        return f(*args, **kwargs)
    return decorated


@books_bp.route('/')
@books_bp.route('/dashboard')
@login_required
def dashboard():
    total_books    = Book.query.count()
    total_issued   = Issue.query.filter(Issue.status.in_(['issued', 'pending_return'])).count()
    overdue_count  = sum(1 for i in Issue.query.filter(
                         Issue.status.in_(['issued', 'pending_return'])).all() if i.is_overdue())
    pending_count  = Issue.query.filter_by(status='pending_return').count()

    recent_issues = (
        Issue.query.filter_by(user_id=current_user.id)
        .order_by(Issue.issue_date.desc())
        .limit(5)
        .all()
    )
    return render_template(
        'dashboard.html',
        total_books=total_books,
        total_issued=total_issued,
        overdue_count=overdue_count,
        pending_count=pending_count,
        recent_issues=recent_issues,
    )


@books_bp.route('/list')
@login_required
def list_books():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    books_query = Book.query
    if query:
        books_query = books_query.filter(
            (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
        )
    if category:
        books_query = books_query.filter(Book.category.ilike(f'%{category}%'))

    books = books_query.order_by(Book.title).all()
    categories = db.session.query(Book.category).distinct().all()
    return render_template('books.html', books=books, query=query, categories=categories, selected_category=category)


@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        category = request.form.get('category', '').strip()
        copies = int(request.form.get('copies', 1))

        if not title or not author or not isbn:
            flash('Title, author, and ISBN are required.', 'danger')
            return render_template('books.html', show_form=True)

        if Book.query.filter_by(isbn=isbn).first():
            flash('A book with that ISBN already exists.', 'danger')
            return render_template('books.html', show_form=True)

        book = Book(
            title=title, author=author, isbn=isbn,
            category=category, total_copies=copies, available_copies=copies
        )
        db.session.add(book)
        db.session.commit()
        flash(f'"{title}" added successfully.', 'success')
        return redirect(url_for('books.list_books'))

    return render_template('books.html', show_form=True)


@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if Issue.query.filter(Issue.book_id == book_id,
                          Issue.status.in_(['issued', 'pending_return'])).count() > 0:
        flash('Cannot delete: book has active or pending issues.', 'danger')
    else:
        db.session.delete(book)
        db.session.commit()
        flash(f'"{book.title}" deleted.', 'success')
    return redirect(url_for('books.list_books'))
