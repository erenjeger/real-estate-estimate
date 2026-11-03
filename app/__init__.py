import click
from flask import Flask

from .config import Config
from .extensions import db, migrate


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401
    from .routes import main

    app.register_blueprint(main)

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables for a fresh local installation."""
        with app.app_context():
            db.create_all()
        click.echo("Database tables created.")

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
