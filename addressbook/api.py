"""JSON HTTP API used by the single-page front end."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_file

from . import repository as repo
from .excel_io import ExcelImportError, export_workbook, parse_workbook, template_workbook
from .repository import ValidationError, identifiers, name_key

bp = Blueprint("api", __name__)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _error(message: str, status: int = 400, fields: dict | None = None):
    return jsonify({"error": {"message": message, "fields": fields or {}}}), status


def _flag(value) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@bp.get("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now(timezone.utc).isoformat()})


@bp.get("/contacts")
def list_contacts():
    contacts = repo.list_contacts(
        query=request.args.get("q", ""),
        bookmarked=_flag(request.args.get("bookmarked")),
        tag=request.args.get("tag", ""),
    )
    return jsonify({"contacts": contacts, "count": len(contacts)})


@bp.post("/contacts")
def create_contact():
    payload = request.get_json(silent=True)
    try:
        contact = repo.create_contact(payload)
    except ValidationError as exc:
        return _error(exc.message, 400, exc.fields)
    return jsonify({"contact": contact}), 201


@bp.get("/contacts/<int:contact_id>")
def get_contact(contact_id: int):
    contact = repo.get_contact(contact_id)
    if contact is None:
        return _error("联系人不存在", 404)
    return jsonify({"contact": contact})


@bp.put("/contacts/<int:contact_id>")
def update_contact(contact_id: int):
    payload = request.get_json(silent=True)
    try:
        contact = repo.update_contact(contact_id, payload)
    except ValidationError as exc:
        return _error(exc.message, 400, exc.fields)
    if contact is None:
        return _error("联系人不存在", 404)
    return jsonify({"contact": contact})


@bp.delete("/contacts/<int:contact_id>")
def delete_contact(contact_id: int):
    if not repo.delete_contact(contact_id):
        return _error("联系人不存在", 404)
    return jsonify({"deleted": True, "id": contact_id})


@bp.patch("/contacts/<int:contact_id>/bookmark")
def toggle_bookmark(contact_id: int):
    payload = request.get_json(silent=True) or {}
    requested = payload.get("bookmarked")
    result = repo.set_bookmark(contact_id, None if requested is None else bool(requested))
    if result is None:
        return _error("联系人不存在", 404)
    return jsonify(result)


@bp.get("/meta")
def meta():
    return jsonify({"tags": repo.tags_summary(), "stats": repo.stats()})


@bp.get("/export")
def export_contacts():
    contacts = repo.list_contacts(
        query=request.args.get("q", ""),
        bookmarked=_flag(request.args.get("bookmarked")),
        tag=request.args.get("tag", ""),
    )
    if not contacts:
        return _error("当前筛选结果为空，没有可导出的联系人", 400)
    buffer = export_workbook(contacts)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    return send_file(
        buffer,
        mimetype=XLSX_MIME,
        as_attachment=True,
        download_name=f"folio-contacts-{stamp}.xlsx",
    )


@bp.get("/import/template")
def import_template():
    buffer = template_workbook()
    return send_file(
        buffer,
        mimetype=XLSX_MIME,
        as_attachment=True,
        download_name="folio-import-template.xlsx",
    )


@bp.post("/import/preview")
def import_preview():
    upload = request.files.get("file")
    if upload is None or not upload.filename:
        return _error("请选择要导入的 Excel 文件")
    filename = upload.filename
    if not filename.lower().endswith((".xlsx", ".xlsm")):
        return _error("仅支持 .xlsx 格式的 Excel 文件")
    try:
        result = parse_workbook(upload.stream, filename)
    except ExcelImportError as exc:
        return _error(str(exc), 400)
    return jsonify(result)


@bp.post("/import")
def import_contacts():
    payload = request.get_json(silent=True) or {}
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        return _error("没有可导入的数据")
    if len(rows) > 1000:
        return _error("单次最多导入 1000 条联系人")

    accepted: list[dict] = []
    skipped: list[dict] = []
    failed: list[dict] = []
    batch_seen: list[tuple[int, str, str, set[str], set[str]]] = []

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or not row.get("selected", True):
            continue
        try:
            data = repo.validate_contact(row.get("contact"))
        except ValidationError as exc:
            failed.append({"index": index, "message": exc.message})
            continue

        existing = repo.find_duplicate(data)
        if existing is not None:
            skipped.append({"index": index, "name": data["name"], "reason": f"与「{existing['name']}」重复"})
            continue

        phones, emails = identifiers(data)
        duplicate_row = None
        for seen_index, seen_name, seen_key, seen_phones, seen_emails in batch_seen:
            if phones & seen_phones or emails & seen_emails:
                duplicate_row = (seen_index, seen_name)
                break
            if seen_key == name_key(data["name"]) and not phones and not seen_phones:
                duplicate_row = (seen_index, seen_name)
                break
        if duplicate_row:
            skipped.append({"index": index, "name": data["name"], "reason": f"与本批次第 {duplicate_row[0]} 条「{duplicate_row[1]}」重复"})
            continue

        batch_seen.append((index, data["name"], name_key(data["name"]), phones, emails))
        accepted.append(data)

    if accepted:
        repo.bulk_create(accepted)

    return jsonify(
        {
            "imported": len(accepted),
            "skipped": len(skipped),
            "failed": len(failed),
            "skippedDetails": skipped,
            "failedDetails": failed,
        }
    )