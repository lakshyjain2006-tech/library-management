from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.book import Book
from models.issue import Issue
from models.user import User
from datetime import datetime
from functools import wraps

issues_bp = Blueprint('issues', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('books.dashboard'))
        return f(*args, **kwargs)
    return decorated


# ── Issue a book (admin only) ────────────────────────────────────────────────
@issues_bp.route('/issue', methods=['GET', 'POST'])
@login_required
@admin_required
def issue_book():
    books   = Book.query.filter(Book.available_copies > 0).order_by(Book.title).all()
    members = User.query.filter_by(role='member').order_by(User.username).all()

    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        user_id = request.form.get('user_id', type=int)

        if not book_id or not user_id:
            flash('Please select both a member and a book.', 'danger')
            return render_template('issue_book.html', books=books, members=members)

        book = Book.query.get_or_404(book_id)

        if not book.is_available():
            flash('No copies available for this book.', 'danger')
            return redirect(url_for('issues.issue_book'))

        existing = Issue.query.filter(
            Issue.user_id == user_id,
            Issue.book_id == book_id,
            Issue.status.in_(['issued', 'pending_return'])
        ).first()
        if existing:
            flash('This book is already issued to that member.', 'warning')
            return redirect(url_for('issues.issue_book'))

        issue = Issue(user_id=user_id, book_id=book_id)
        book.available_copies -= 1
        db.session.add(issue)
        db.session.commit()
        flash(f'"{book.title}" issued successfully.', 'success')
        return redirect(url_for('books.dashboard'))

    return render_template('issue_book.html', books=books, members=members)


# ── Member requests a return (sets status → pending_return) ─────────────────
@issues_bp.route('/request-return/<int:issue_id>', methods=['POST'])
@login_required
def request_return(issue_id):
    issue = Issue.query.get_or_404(issue_id)

    # Members can only act on their own issues
    if not current_user.is_admin() and issue.user_id != current_user.id:
        flash('Unauthorised action.', 'danger')
        return redirect(url_for('books.dashboard'))

    if issue.status != 'issued':
        flash('This book is not in an issued state.', 'warning')
        return redirect(url_for('issues.my_issues'))

    issue.status = 'pending_return'
    # Record when the member said they returned it
    issue.return_date = datetime.utcnow()
    db.session.commit()

    flash('Return request submitted. Waiting for admin to verify and confirm.', 'info')
    return redirect(url_for('issues.my_issues'))


# ── Admin confirms the physical return ──────────────────────────────────────
@issues_bp.route('/confirm-return/<int:issue_id>', methods=['POST'])
@login_required
@admin_required
def confirm_return(issue_id):
    issue = Issue.query.get_or_404(issue_id)

    if issue.status != 'pending_return':
        flash('This issue is not awaiting return verification.', 'warning')
        return redirect(url_for('issues.pending_returns'))

    issue.status      = 'returned'
    issue.return_date = datetime.utcnow()   # use admin confirmation time as official date
    issue.fine        = issue.calculate_fine()
    issue.book.available_copies += 1
    db.session.commit()

    if issue.fine > 0:
        flash(
            f'Return confirmed for "{issue.book.title}" '
            f'(member: {issue.user.username}). '
            f'Overdue fine: ₹{issue.fine:.2f}',
            'warning'
        )
    else:
        flash(
            f'Return confirmed for "{issue.book.title}" '
            f'(member: {issue.user.username}). No fine.',
            'success'
        )
    return redirect(url_for('issues.pending_returns'))


# ── Admin rejects the return request (puts book back to issued) ──────────────
@issues_bp.route('/reject-return/<int:issue_id>', methods=['POST'])
@login_required
@admin_required
def reject_return(issue_id):
    issue = Issue.query.get_or_404(issue_id)

    if issue.status != 'pending_return':
        flash('This issue is not awaiting return verification.', 'warning')
        return redirect(url_for('issues.pending_returns'))

    issue.status      = 'issued'
    issue.return_date = None          # wipe the provisional return date
    db.session.commit()

    flash(
        f'Return request for "{issue.book.title}" rejected. '
        f'Book is back to issued for {issue.user.username}.',
        'danger'
    )
    return redirect(url_for('issues.pending_returns'))


# ── Admin: list all pending return requests ──────────────────────────────────
@issues_bp.route('/pending-returns')
@login_required
@admin_required
def pending_returns():
    pending = (
        Issue.query
        .filter_by(status='pending_return')
        .order_by(Issue.return_date.asc())
        .all()
    )
    return render_template('pending_returns.html', pending=pending)


# ── Admin: all issues (with status filter) ───────────────────────────────────
@issues_bp.route('/all')
@login_required
@admin_required
def all_issues():
    status_filter = request.args.get('status', 'all')
    q = Issue.query
    if status_filter == 'issued':
        q = q.filter_by(status='issued')
    elif status_filter == 'pending':
        q = q.filter_by(status='pending_return')
    elif status_filter == 'returned':
        q = q.filter_by(status='returned')
    issues = q.order_by(Issue.issue_date.desc()).all()
    return render_template(
        'issue_book.html',
        issues=issues,
        status_filter=status_filter,
        view='all'
    )


# ── Member: my issues ────────────────────────────────────────────────────────
@issues_bp.route('/my')
@login_required
def my_issues():
    issues = (
        Issue.query
        .filter_by(user_id=current_user.id)
        .order_by(Issue.issue_date.desc())
        .all()
    )
    return render_template('issue_book.html', issues=issues, view='my')
