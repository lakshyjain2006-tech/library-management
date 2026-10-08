import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.issues import issues_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(issues_bp, url_prefix='/issues')

    # Create tables and seed default admin
    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Create a default admin account if none exists."""

    if not User.query.filter_by(role='admin').first():

        admin_username = os.environ.get(
            "ADMIN_USERNAME",
            "admin"
        )

        admin_password = os.environ.get(
            "ADMIN_PASSWORD",
            "Admin@123"
        )

        admin_email = os.environ.get(
            "ADMIN_EMAIL",
            "admin@library.com"
        )

        admin = User(
            username=admin_username,
            email=admin_email,
            role='admin'
        )

        admin.set_password(admin_password)

        db.session.add(admin)
        db.session.commit()

        print(
            f"[INFO] Default admin created → "
            f"username: {admin_username}"
        )


from flask import redirect, url_for

# your create_app() function above this

app = create_app()


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)
