"""Application factory for Folio Address Book."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path

import click
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from . import db

# Windows can map .js to text/plain in the registry; browsers then refuse to
# execute the file because of X-Content-Type-Options: nosniff.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")

APP_NAME = "Folio 通讯录"


def create_app(test_config: dict | None = None) -> Flask:
    package_root = Path(__file__).resolve().parent
    project_root = package_root.parent
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    database = os.environ.get("ADDRESSBOOK_DB") or str(Path(app.instance_path) / "addressbook.sqlite3")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-secret-change-me"),
        DATABASE=database,
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    app.json.ensure_ascii = False
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.init_db()

    from .api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return render_template("index.html", app_name=APP_NAME)

    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": {"message": "文件过大，最大支持 8 MB"}}), 413
        return "Request entity too large", 413

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": {"message": "接口不存在"}}), 404
        return render_template("index.html", app_name=APP_NAME), 404

    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Insert a small demo data set (only when the book is empty)."""
        from .seed import seed_demo_data

        inserted = seed_demo_data()
        if inserted:
            click.echo(f"Inserted {inserted} demo contacts.")
        else:
            click.echo("Address book is not empty; nothing inserted.")

    return app