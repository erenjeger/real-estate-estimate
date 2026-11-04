import click
import hashlib
from pathlib import Path

from flask import Flask

from .config import Config
from .extensions import db, migrate


def format_idr(value):
    from decimal import Decimal, InvalidOperation

    try:
        amount = Decimal(str(value)).quantize(Decimal("1"))
    except (InvalidOperation, TypeError, ValueError):
        return "Rp 0"
    return f"Rp {amount:,}".replace(",", ".")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.add_template_filter(format_idr, "idr")

    @app.context_processor
    def asset_version():
        def version_for(filename):
            try:
                content = (Path(app.static_folder) / filename).read_bytes()
            except OSError:
                return "0"
            return hashlib.md5(content).hexdigest()[:10]

        return {"asset_version": version_for}

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
