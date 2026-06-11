from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    from models import User

    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return (
            '<h1>Find Job</h1>'
            '<p>Phase 3 auth scaffold is ready.</p>'
            '<p><a href="/register">Get Started</a> | <a href="/login">Login</a></p>'
        )

    return app
