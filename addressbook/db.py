"""SQLite helpers: connection management and schema creation."""

from __future__ import annotations

import sqlite3

import click
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    company       TEXT    NOT NULL DEFAULT '',
    job_title     TEXT    NOT NULL DEFAULT '',
    notes         TEXT    NOT NULL DEFAULT '',
    tags          TEXT    NOT NULL DEFAULT '',
    is_bookmarked INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL,
    updated_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS contact_methods (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL REFERENCES contacts (id) ON DELETE CASCADE,
    kind       TEXT    NOT NULL,
    label      TEXT    NOT NULL DEFAULT '',
    value      TEXT    NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_contacts_name      ON contacts (name);
CREATE INDEX IF NOT EXISTS idx_contacts_bookmark  ON contacts (is_bookmarked);
CREATE INDEX IF NOT EXISTS idx_methods_contact    ON contact_methods (contact_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_methods_value      ON contact_methods (value);
"""


def get_db() -> sqlite3.Connection:
    """Return the request-scoped connection, creating it on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
            timeout=10,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
    return g.db


def close_db(exception: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create missing tables. Idempotent, so it is safe on every boot."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


@click.command("init-db")
def init_db_command() -> None:
    """Create the database tables."""
    init_db()
    click.echo(f"Initialised database at {current_app.config['DATABASE']}")


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)