"""Domain logic for contacts, their contact methods, tags and bookmarks."""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone

from .db import get_db

KINDS = ("phone", "email", "wechat", "qq", "address", "other")
MAX_METHODS = 30
MAX_TAGS = 8
NAME_LIMIT = 80
SHORT_LIMIT = 80
NOTES_LIMIT = 2000
VALUE_LIMIT = 200
LABEL_LIMIT = 40

_TAG_SPLIT = re.compile(r"[,，;；]")


class ValidationError(ValueError):
    """Raised when a contact payload cannot be accepted."""

    def __init__(self, message: str, fields: dict[str, str] | None = None, errors: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.fields = fields or {}
        self.errors = errors or [message]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_tags(raw) -> list[str]:
    """Accept a list or a delimited string; return unique, trimmed tags."""
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = _TAG_SPLIT.split(raw)
    elif isinstance(raw, (list, tuple)):
        parts = []
        for item in raw:
            if isinstance(item, str):
                parts.extend(_TAG_SPLIT.split(item))
    else:
        parts = []
    tags: list[str] = []
    seen: set[str] = set()
    for part in parts:
        tag = part.strip()
        if not tag:
            continue
        tag = tag[:24]
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        tags.append(tag)
        if len(tags) >= MAX_TAGS:
            break
    return tags


def _as_text(value, limit: int) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value).strip()
    return text[:limit]


def _as_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().casefold()
    if text in {"1", "true", "yes", "y", "on", "是", "书签", "收藏"}:
        return True
    if text in {"0", "false", "no", "n", "off", "否", ""}:
        return False
    return default


def _store_tags(tags: list[str]) -> str:
    return f",{','.join(tags)}," if tags else ""


def _load_tags(stored: str) -> list[str]:
    return [tag for tag in stored.strip(",").split(",") if tag]


def _validate_methods(raw_methods) -> list[dict]:
    if raw_methods is None:
        return []
    if not isinstance(raw_methods, list):
        raise ValidationError("联系方式格式不正确", {"methods": "联系方式格式不正确"})
    if len(raw_methods) > MAX_METHODS:
        raise ValidationError(
            f"联系方式最多 {MAX_METHODS} 条",
            {"methods": f"联系方式最多 {MAX_METHODS} 条"},
        )
    cleaned: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(raw_methods, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f"第 {index} 条联系方式格式不正确", {"methods": f"第 {index} 条联系方式格式不正确"})
        kind = str(item.get("kind", "")).strip().lower()
        if kind not in KINDS:
            raise ValidationError(f"第 {index} 条联系方式的类型不受支持", {"methods": f"第 {index} 条联系方式的类型不受支持"})
        value = _as_text(item.get("value"), VALUE_LIMIT)
        if not value:
            raise ValidationError(f"第 {index} 条联系方式缺少内容", {"methods": f"第 {index} 条联系方式缺少内容"})
        label = _as_text(item.get("label"), LABEL_LIMIT)
        if kind == "other" and not label:
            label = "其他"
        key = (kind, value.casefold())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({"kind": kind, "label": label, "value": value})
    return cleaned


def validate_contact(payload) -> dict:
    """Validate and normalise a contact payload; raise ValidationError."""
    if not isinstance(payload, dict):
        raise ValidationError("请求内容格式不正确")

    name = _as_text(payload.get("name"), NAME_LIMIT)
    if not name:
        raise ValidationError("请填写联系人姓名", {"name": "请填写联系人姓名"})

    data = {
        "name": name,
        "company": _as_text(payload.get("company"), SHORT_LIMIT),
        "job_title": _as_text(payload.get("jobTitle", payload.get("job_title")), SHORT_LIMIT),
        "notes": _as_text(payload.get("notes"), NOTES_LIMIT),
        "tags": normalize_tags(payload.get("tags")),
        "bookmarked": _as_bool(payload.get("bookmarked")),
        "methods": _validate_methods(payload.get("methods")),
    }
    return data


def _method_rows(db: sqlite3.Connection, contact_ids: list[int]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {cid: [] for cid in contact_ids}
    if not contact_ids:
        return grouped
    placeholders = ",".join("?" for _ in contact_ids)
    rows = db.execute(
        f"""SELECT id, contact_id, kind, label, value
            FROM contact_methods
            WHERE contact_id IN ({placeholders})
            ORDER BY sort_order ASC, id ASC""",
        contact_ids,
    ).fetchall()
    for row in rows:
        grouped[row["contact_id"]].append(
            {
                "id": row["id"],
                "kind": row["kind"],
                "label": row["label"],
                "value": row["value"],
            }
        )
    return grouped


def _serialise(row: sqlite3.Row, methods: list[dict]) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "company": row["company"],
        "jobTitle": row["job_title"],
        "notes": row["notes"],
        "tags": _load_tags(row["tags"]),
        "bookmarked": bool(row["is_bookmarked"]),
        "methods": methods,
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def _like_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_contacts(query: str = "", bookmarked: bool = False, tag: str = "") -> list[dict]:
    db = get_db()
    sql = ["SELECT c.* FROM contacts c WHERE 1 = 1"]
    params: list = []

    query = (query or "").strip()
    if query:
        pattern = f"%{_like_escape(query)}%"
        sql.append(
            """AND (
                lower(c.name) LIKE lower(?) ESCAPE '\\'
                OR lower(c.company) LIKE lower(?) ESCAPE '\\'
                OR lower(c.job_title) LIKE lower(?) ESCAPE '\\'
                OR lower(c.notes) LIKE lower(?) ESCAPE '\\'
                OR lower(c.tags) LIKE lower(?) ESCAPE '\\'
                OR EXISTS (
                    SELECT 1 FROM contact_methods m
                    WHERE m.contact_id = c.id
                      AND lower(m.value) LIKE lower(?) ESCAPE '\\'
                )
            )"""
        )
        params.extend([pattern] * 6)

    if bookmarked:
        sql.append("AND c.is_bookmarked = 1")

    tag = (tag or "").strip()
    if tag:
        sql.append("AND c.tags LIKE ? ESCAPE '\\'")
        params.append(f"%,{_like_escape(tag)},%")

    sql.append("ORDER BY c.is_bookmarked DESC, c.name COLLATE NOCASE ASC, c.id ASC")
    rows = db.execute(" ".join(sql), params).fetchall()
    methods = _method_rows(db, [row["id"] for row in rows])
    return [_serialise(row, methods[row["id"]]) for row in rows]


def get_contact(contact_id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        return None
    return _serialise(row, _method_rows(db, [row["id"]])[row["id"]])


def _insert_contact(db: sqlite3.Connection, data: dict, timestamp: str | None = None) -> int:
    now = timestamp or utc_now()
    cursor = db.execute(
        """INSERT INTO contacts (name, company, job_title, notes, tags, is_bookmarked, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"],
            data["company"],
            data["job_title"],
            data["notes"],
            _store_tags(data["tags"]),
            1 if data["bookmarked"] else 0,
            now,
            now,
        ),
    )
    contact_id = int(cursor.lastrowid)
    _replace_methods(db, contact_id, data["methods"])
    return contact_id


def _replace_methods(db: sqlite3.Connection, contact_id: int, methods: list[dict]) -> None:
    db.execute("DELETE FROM contact_methods WHERE contact_id = ?", (contact_id,))
    db.executemany(
        """INSERT INTO contact_methods (contact_id, kind, label, value, sort_order)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (contact_id, method["kind"], method["label"], method["value"], index)
            for index, method in enumerate(methods)
        ],
    )


def create_contact(payload) -> dict:
    data = validate_contact(payload)
    db = get_db()
    contact_id = _insert_contact(db, data)
    db.commit()
    return get_contact(contact_id)


def update_contact(contact_id: int, payload) -> dict | None:
    db = get_db()
    existing = db.execute("SELECT id FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if existing is None:
        return None
    data = validate_contact(payload)
    db.execute(
        """UPDATE contacts
           SET name = ?, company = ?, job_title = ?, notes = ?, tags = ?,
               is_bookmarked = ?, updated_at = ?
           WHERE id = ?""",
        (
            data["name"],
            data["company"],
            data["job_title"],
            data["notes"],
            _store_tags(data["tags"]),
            1 if data["bookmarked"] else 0,
            utc_now(),
            contact_id,
        ),
    )
    _replace_methods(db, contact_id, data["methods"])
    db.commit()
    return get_contact(contact_id)


def set_bookmark(contact_id: int, bookmarked: bool | None = None) -> dict | None:
    db = get_db()
    row = db.execute("SELECT id, is_bookmarked FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        return None
    new_value = (not bool(row["is_bookmarked"])) if bookmarked is None else bool(bookmarked)
    db.execute(
        "UPDATE contacts SET is_bookmarked = ?, updated_at = ? WHERE id = ?",
        (1 if new_value else 0, utc_now(), contact_id),
    )
    db.commit()
    return {"id": contact_id, "bookmarked": new_value}


def delete_contact(contact_id: int) -> bool:
    db = get_db()
    cursor = db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    db.commit()
    return cursor.rowcount > 0


def tags_summary() -> list[dict]:
    db = get_db()
    rows = db.execute("SELECT tags FROM contacts").fetchall()
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update(_load_tags(row["tags"]))
    return [
        {"name": name, "count": count}
        for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold()))
    ]


def stats() -> dict:
    db = get_db()
    row = db.execute(
        """SELECT COUNT(*) AS total,
                  COALESCE(SUM(is_bookmarked), 0) AS bookmarked
           FROM contacts"""
    ).fetchone()
    methods = db.execute("SELECT COUNT(*) AS n FROM contact_methods").fetchone()["n"]
    return {"total": row["total"], "bookmarked": row["bookmarked"], "methods": methods, "tags": len(tags_summary())}


def name_key(name: str) -> str:
    return re.sub(r"\s+", "", name or "").casefold()


def identifiers(contact: dict) -> tuple[set[str], set[str]]:
    phones: set[str] = set()
    emails: set[str] = set()
    for method in contact.get("methods") or []:
        if method.get("kind") == "phone":
            digits = re.sub(r"\D", "", str(method.get("value", "")))
            if len(digits) >= 6:
                phones.add(digits)
        elif method.get("kind") == "email":
            emails.add(str(method.get("value", "")).strip().casefold())
    return phones, emails


def find_duplicate(contact: dict, exclude_id: int | None = None) -> dict | None:
    """Return an existing contact that looks like the same person."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM contacts WHERE (? IS NULL OR id <> ?)",
        (exclude_id, exclude_id),
    ).fetchall()
    methods = _method_rows(db, [row["id"] for row in rows])
    phones, emails = identifiers(contact)
    key = name_key(contact.get("name", ""))
    name_match: dict | None = None
    for row in rows:
        existing = _serialise(row, methods[row["id"]])
        other_phones, other_emails = identifiers(existing)
        if phones & other_phones:
            return {"id": existing["id"], "name": existing["name"], "reason": "phone"}
        if emails & other_emails:
            return {"id": existing["id"], "name": existing["name"], "reason": "email"}
        if name_key(existing["name"]) == key:
            name_match = {"id": existing["id"], "name": existing["name"], "reason": "name"}
            if not phones and not other_phones and not emails and not other_emails:
                return name_match
    return None


def bulk_create(validated: list[dict]) -> list[int]:
    """Insert many already-validated contacts in a single transaction."""
    db = get_db()
    ids: list[int] = []
    now = utc_now()
    try:
        db.execute("BEGIN")
        for data in validated:
            ids.append(_insert_contact(db, data, timestamp=now))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return ids