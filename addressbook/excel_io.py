"""Excel import/export for the address book (openpyxl).

Export layout (one row per contact, one labelled column per value):
    Name | Company | Job Title | Tags | Bookmarked |
    Phone 1..n | Email 1..n | WeChat 1..n | Social 1..n | Address 1..n |
    Other 1 Type | Other 1 Value | ... | Notes

Import reads that layout by header name, tolerates re-ordered or extra
columns, accepts Chinese or English headers and splits multi-value cells
on semicolons.  A second "Read Me" sheet documents the format.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date, datetime
from io import BytesIO

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from .repository import (
    ValidationError,
    find_duplicate,
    identifiers,
    name_key,
    normalize_tags,
    utc_now,
    validate_contact,
)

KIND_ORDER = ("phone", "email", "wechat", "qq", "address")
KIND_LABELS = {
    "phone": "Phone",
    "email": "Email",
    "wechat": "WeChat",
    "qq": "Social",
    "address": "Address",
}
BASE_FIELDS = ("name", "company", "job_title", "tags", "bookmarked")
MAX_IMPORT_ROWS = 1000

# ---------------------------------------------------------------- reading ----

_BASE_ALIASES = {
    "name": {"name", "full name", "contact name", "姓名", "名字", "联系人", "联系人姓名"},
    "company": {"company", "organization", "organisation", "org", "公司", "单位", "公司名称"},
    "job_title": {"job title", "title", "position", "role", "职位", "职务", "岗位"},
    "tags": {"tags", "tag", "标签", "分组"},
    "bookmarked": {"bookmarked", "bookmark", "favorite", "favourite", "书签", "收藏"},
    "notes": {"notes", "note", "remark", "remarks", "备注", "说明"},
}

_METHOD_ALIASES = {
    "phone": "phone",
    "tel": "phone",
    "telephone": "phone",
    "mobile": "phone",
    "cell": "phone",
    "电话": "phone",
    "手机": "phone",
    "手机号": "phone",
    "电话号码": "phone",
    "email": "email",
    "e mail": "email",
    "mail": "email",
    "邮箱": "email",
    "电子邮箱": "email",
    "wechat": "wechat",
    "we chat": "wechat",
    "weixin": "wechat",
    "微信": "wechat",
    "qq": "qq",
    "social": "qq",
    "im": "qq",
    "社交": "qq",
    "address": "address",
    "住址": "address",
    "地址": "address",
}

_METHOD_RE = re.compile(
    r"^(?P<kind>phone|tel|telephone|mobile|cell|email|e mail|mail|wechat|we chat|weixin|qq|social|im|address|"
    r"电话|手机|手机号|电话号码|邮箱|电子邮箱|微信|住址|地址)\s*(?:no\.?|#)?\s*(?P<index>\d+)?$"
)
_OTHER_TYPE_RE = re.compile(r"^(?:other|其他)\s*(?P<index>\d+)?\s*(?:type|类型)$")
_OTHER_VALUE_RE = re.compile(r"^(?:other|其他)\s*(?P<index>\d+)?\s*(?:value|值|内容|号码)$")


def _norm_header(value) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("_", " ").replace("-", " ")
    text = text.replace("：", " ").replace(":", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _header_specs(headers) -> dict[int, tuple]:
    """Map column index -> ('base', field) / ('method', kind) / ('other', idx, part)."""
    specs: dict[int, tuple] = {}
    for index, raw in enumerate(headers):
        header = _norm_header(raw)
        if not header:
            continue
        for field, aliases in _BASE_ALIASES.items():
            if header in aliases:
                specs[index] = ("base", field)
                break
        else:
            match = _OTHER_TYPE_RE.match(header)
            if match:
                specs[index] = ("other", int(match.group("index") or 1), "type")
                continue
            match = _OTHER_VALUE_RE.match(header)
            if match:
                specs[index] = ("other", int(match.group("index") or 1), "value")
                continue
            match = _METHOD_RE.match(header)
            if match:
                specs[index] = ("method", _METHOD_ALIASES[match.group("kind")])
    return specs


def _cell_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _split_values(value) -> list[str]:
    text = _cell_text(value)
    if not text:
        return []
    parts = re.split(r"[;；\n]+", text)
    return [part.strip() for part in parts if part.strip()]


def _parse_bookmarked(value) -> tuple[bool, str | None]:
    if value is None or _cell_text(value) == "":
        return False, None
    text = _cell_text(value).casefold()
    if text in {"1", "true", "yes", "y", "是", "书签", "收藏"}:
        return True, None
    if text in {"0", "false", "no", "n", "否"}:
        return False, None
    return False, f"“{_cell_text(value)}”不是有效的书签值，已按“否”处理"


def _find_header(rows: list[tuple]) -> tuple[int, dict[int, tuple]] | None:
    best: tuple[int, dict[int, tuple]] | None = None
    best_score = 0
    for index, row in enumerate(rows[:15]):
        specs = _header_specs(row)
        fields = {spec[1] for spec in specs.values() if spec[0] == "base"}
        score = len(specs)
        if "name" in fields and score >= 2 and score > best_score:
            best = (index, specs)
            best_score = score
    return best


def _pick_sheet(workbook):
    preferred = None
    for sheet in workbook.worksheets:
        if sheet.title.strip().casefold() in {"contacts", "联系人", "通讯录"}:
            preferred = sheet
            break
    candidates = [preferred] if preferred is not None else []
    candidates += [sheet for sheet in workbook.worksheets if sheet is not preferred]
    for sheet in candidates:
        max_row = sheet.max_row or 1
        rows = list(sheet.iter_rows(values_only=True, max_row=min(max_row, 15)))
        header = _find_header(rows)
        if header:
            return sheet, rows, header
    raise ExcelImportError(
        "没有找到可识别的表头。请确认第一张工作表包含 Name（姓名）列，"
        "或先下载导入模板。"
    )


class ExcelImportError(ValueError):
    """Raised when a workbook cannot be interpreted."""


def parse_workbook(stream, filename: str = "contacts.xlsx") -> dict:
    """Parse an .xlsx file (binary stream) into a preview payload."""
    try:
        stream.seek(0)
    except (AttributeError, OSError):
        pass
    try:
        workbook = load_workbook(stream, read_only=True, data_only=True)
    except Exception as exc:  # openpyxl raises several types for corrupt files
        raise ExcelImportError("无法读取该文件，请上传 .xlsx 格式的 Excel 文件。") from exc

    try:
        sheet, _head_rows, (header_index, specs) = _pick_sheet(workbook)
        sheet_title = sheet.title
        if (sheet.max_row or 0) > MAX_IMPORT_ROWS + header_index + 20:
            raise ExcelImportError(f"单次最多导入 {MAX_IMPORT_ROWS} 行数据，请拆分文件后重试。")

        preview_rows: list[dict] = []
        seen: list[tuple[int, str, str, set[str], set[str]]] = []
        counts = Counter()

        for offset, row in enumerate(sheet.iter_rows(values_only=True, min_row=header_index + 2), start=header_index + 2):
            if offset > header_index + MAX_IMPORT_ROWS + 1:
                break
            if not any(_cell_text(cell) for cell in row):
                continue
            preview_rows.append(_parse_row(row, specs, offset, seen, counts))
    finally:
        workbook.close()

    if not preview_rows:
        raise ExcelImportError("表格中没有数据行，请在表头下方填写联系人后重试。")

    return {
        "filename": filename,
        "sheet": sheet_title,
        "rows": preview_rows,
        "summary": {
            "total": len(preview_rows),
            "ready": counts["ok"],
            "duplicates": counts["duplicate"],
            "errors": counts["error"],
        },
    }


def _parse_row(row, specs, row_number, seen, counts) -> dict:
    raw_methods: list[dict] = []
    others: dict[int, dict[str, str]] = {}
    data: dict = {
        "name": "",
        "company": "",
        "jobTitle": "",
        "tags": [],
        "bookmarked": False,
        "notes": "",
        "methods": [],
    }
    messages: list[str] = []
    has_error = False

    for index, spec in specs.items():
        value = row[index] if index < len(row) else None
        if spec[0] == "base":
            field = spec[1]
            if field == "tags":
                data["tags"] = normalize_tags(_cell_text(value))
            elif field == "bookmarked":
                bookmarked, warning = _parse_bookmarked(value)
                data["bookmarked"] = bookmarked
                if warning:
                    messages.append(warning)
            else:
                data[field] = _cell_text(value)
        elif spec[0] == "method":
            for part in _split_values(value):
                raw_methods.append({"kind": spec[1], "label": "", "value": part})
        else:  # other
            _, other_index, part = spec
            others.setdefault(other_index, {})[part] = _cell_text(value)

    for other in others.values():
        if other.get("value"):
            raw_methods.append(
                {"kind": "other", "label": other.get("type") or "其他", "value": other["value"]}
            )
    data["methods"] = raw_methods

    if not data["name"]:
        messages.append("缺少姓名")
        has_error = True

    validated = None
    try:
        validated = validate_contact(data)
    except ValidationError as exc:
        messages.extend(exc.errors)
        has_error = True

    status = "ok"
    duplicate_of = None
    if not has_error and validated is not None:
        existing = find_duplicate(validated)
        if existing:
            reason = {"phone": "电话号码", "email": "邮箱地址", "name": "姓名"}.get(existing["reason"], "信息")
            messages.append(f"与已有联系人「{existing['name']}」{reason}相同")
            status = "duplicate"
            duplicate_of = existing
        else:
            phones, emails = identifiers(validated)
            for prev_row, prev_name, prev_key, prev_phones, prev_emails in seen:
                if phones & prev_phones:
                    messages.append(f"与本文件第 {prev_row} 行「{prev_name}」电话号码相同")
                    status = "duplicate"
                    break
                if emails & prev_emails:
                    messages.append(f"与本文件第 {prev_row} 行「{prev_name}」邮箱相同")
                    status = "duplicate"
                    break
                if prev_key == name_key(validated["name"]) and not phones and not prev_phones:
                    messages.append(f"与本文件第 {prev_row} 行「{prev_name}」姓名相同")
                    status = "duplicate"
                    break
            if status == "ok":
                seen.append((row_number, validated["name"], name_key(validated["name"]), phones, emails))

    if has_error:
        status = "error"
    counts[status] += 1

    contact = validated or {
        "name": data["name"],
        "company": data["company"],
        "jobTitle": data["jobTitle"],
        "tags": data["tags"],
        "bookmarked": data["bookmarked"],
        "notes": data["notes"],
        "methods": raw_methods,
    }
    return {
        "row": row_number,
        "status": status,
        "messages": messages,
        "contact": contact,
        "duplicateOf": duplicate_of,
    }


# ---------------------------------------------------------------- writing ----

HEADER_FILL = PatternFill("solid", fgColor="0F766E")
HEADER_FONT = Font(name="Microsoft YaHei", size=11, bold=True, color="FFFFFF")
BODY_FONT = Font(name="Microsoft YaHei", size=10, color="1F2933")
ZEBRA_FILL = PatternFill("solid", fgColor="F6F3EC")
BORDER = Border(
    left=Side(style="thin", color="E2DDD2"),
    right=Side(style="thin", color="E2DDD2"),
    top=Side(style="thin", color="E2DDD2"),
    bottom=Side(style="thin", color="E2DDD2"),
)


class _Layout:
    def __init__(self, contacts: list[dict]):
        self.counts = {kind: 0 for kind in KIND_ORDER}
        self.other_max = 0
        for contact in contacts:
            per_kind = Counter()
            other_count = 0
            for method in contact.get("methods", []):
                kind = method.get("kind")
                if kind in KIND_ORDER:
                    per_kind[kind] += 1
                elif kind == "other":
                    other_count += 1
            for kind in KIND_ORDER:
                self.counts[kind] = max(self.counts[kind], per_kind.get(kind, 0))
            self.other_max = max(self.other_max, other_count)

        self.headers: list[str] = ["Name", "Company", "Job Title", "Tags", "Bookmarked"]
        self.specs: list[tuple] = [
            ("base", "name"),
            ("base", "company"),
            ("base", "jobTitle"),
            ("base", "tags"),
            ("base", "bookmarked"),
        ]
        for kind in KIND_ORDER:
            for slot in range(1, max(self.counts[kind], 1) + 1):
                self.headers.append(f"{KIND_LABELS[kind]} {slot}")
                self.specs.append(("method", kind, slot))
        for slot in range(1, max(self.other_max, 1) + 1):
            self.headers.extend([f"Other {slot} Type", f"Other {slot} Value"])
            self.specs.extend([("otherType", slot), ("otherValue", slot)])
        self.headers.append("Notes")
        self.specs.append(("base", "notes"))

    def row_values(self, contact: dict) -> list:
        by_kind: dict[str, list[dict]] = {kind: [] for kind in KIND_ORDER}
        others: list[dict] = []
        for method in contact.get("methods", []):
            if method.get("kind") in by_kind:
                by_kind[method["kind"]].append(method)
            elif method.get("kind") == "other":
                others.append(method)
        values: list = [
            contact.get("name", ""),
            contact.get("company", ""),
            contact.get("jobTitle", ""),
            ", ".join(contact.get("tags", [])),
            "Yes" if contact.get("bookmarked") else "No",
        ]
        for kind in KIND_ORDER:
            methods = by_kind[kind]
            for slot in range(max(self.counts[kind], 1)):
                values.append(methods[slot]["value"] if slot < len(methods) else "")
        for slot in range(max(self.other_max, 1)):
            method = others[slot] if slot < len(others) else None
            values.append(method.get("label", "") if method else "")
            values.append(method["value"] if method else "")
        values.append(contact.get("notes", ""))
        return values


def _write_sheet(workbook: Workbook, contacts: list[dict]) -> None:
    sheet = workbook.active
    sheet.title = "Contacts"
    sheet.sheet_view.showGridLines = False
    layout = _Layout(contacts)

    for column, header in enumerate(layout.headers, start=1):
        cell = sheet.cell(row=1, column=column, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    sheet.row_dimensions[1].height = 28

    for row_index, contact in enumerate(contacts, start=2):
        for column, value in enumerate(layout.row_values(contact), start=1):
            cell = sheet.cell(row=row_index, column=column, value=value)
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=column == len(layout.headers))
            if layout.specs[column - 1][0] in {"method", "otherValue", "base"} and layout.specs[column - 1] != ("base", "bookmarked"):
                cell.number_format = "@"
            if row_index % 2 == 1:
                cell.fill = ZEBRA_FILL
        sheet.row_dimensions[row_index].height = 24

    for column, header in enumerate(layout.headers, start=1):
        width = 22
        if header in {"Name", "Company", "Job Title"}:
            width = 18 if header != "Company" else 24
        elif header == "Tags":
            width = 20
        elif header == "Bookmarked":
            width = 12
        elif header == "Notes":
            width = 42
        elif header.startswith("Other"):
            width = 16
        sheet.column_dimensions[get_column_letter(column)].width = width

    if contacts:
        last_row = len(contacts) + 1
        sheet.auto_filter.ref = f"A1:{get_column_letter(len(layout.headers))}{last_row}"
        bookmark_column = layout.headers.index("Bookmarked") + 1
        validation = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
        validation.error = "请选择 Yes 或 No"
        validation.errorTitle = "书签格式"
        sheet.add_data_validation(validation)
        validation.add(f"{get_column_letter(bookmark_column)}2:{get_column_letter(bookmark_column)}1000")

    sheet.freeze_panes = "B2"

    readme = workbook.create_sheet("Read Me")
    readme.sheet_view.showGridLines = False
    readme.sheet_properties.tabColor = "C2810B"
    readme.column_dimensions["A"].width = 18
    readme.column_dimensions["B"].width = 96
    title = readme.cell(row=1, column=1, value="Folio 通讯录 · Excel 导入说明")
    title.font = Font(name="Microsoft YaHei", size=16, bold=True, color="0F766E")
    readme.merge_cells("A1:B1")
    readme.row_dimensions[1].height = 32

    notes = [
        ("文件格式", "仅支持 .xlsx。第一张名为 Contacts 的工作表会被导入，本说明页会被忽略。"),
        ("一行一人", "每条联系人占一行；同一类联系方式有多条时，会依次写入 Phone 1、Phone 2… 列。"),
        ("多值拆分", "单元格内使用英文分号 ; 分隔多个电话/邮箱（例如 138…; 139…）会被自动拆成多条。"),
        ("必填字段", "Name 不能为空；其他列均可留空。"),
        ("书签列", "Bookmarked 填 Yes / No（也接受 true / false、是 / 否、1 / 0）。"),
        ("标签列", "Tags 用逗号分隔，例如：客户, 重点。"),
        ("其他方式", "Other 1 Type 填自定义类型（如 LinkedIn），Other 1 Value 填对应内容。"),
        ("电话号码", "建议把电话列设置为“文本”格式，避免 Excel 丢掉开头的 0。"),
        ("重复检测", "导入前会按姓名、电话、邮箱检查重复：重复行默认不导入，可在预览中确认。"),
        ("模板行", "本模板附带两行示例数据，导入前请删除或覆盖。"),
    ]
    row = 3
    for label, text in notes:
        key_cell = readme.cell(row=row, column=1, value=label)
        key_cell.font = Font(name="Microsoft YaHei", size=10, bold=True, color="1F2933")
        key_cell.alignment = Alignment(vertical="top")
        value_cell = readme.cell(row=row, column=2, value=text)
        value_cell.font = Font(name="Microsoft YaHei", size=10, color="4B5563")
        value_cell.alignment = Alignment(vertical="top", wrap_text=True)
        readme.row_dimensions[row].height = 30
        row += 1

    readme.cell(row=row + 1, column=1, value="模板版本").font = BODY_FONT
    readme.cell(row=row + 1, column=2, value=f"v1.0 · {utc_now()[:10]}")


def export_workbook(contacts: list[dict]) -> BytesIO:
    workbook = Workbook()
    _write_sheet(workbook, contacts)
    workbook.properties.title = "Folio Address Book Export"
    workbook.properties.creator = "Folio Address Book"
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def template_workbook() -> BytesIO:
    examples = [
        {
            "name": "林晚晴",
            "company": "星野科技",
            "jobTitle": "产品经理",
            "tags": ["客户", "重点"],
            "bookmarked": True,
            "notes": "季度例会主持人，偏好邮件沟通。",
            "methods": [
                {"kind": "phone", "label": "", "value": "13800138001"},
                {"kind": "phone", "label": "", "value": "0591-88001234"},
                {"kind": "email", "label": "", "value": "wanqing.lin@example.com"},
                {"kind": "wechat", "label": "", "value": "wanqing_l"},
                {"kind": "qq", "label": "", "value": "100200300"},
                {"kind": "address", "label": "", "value": "福建省福州市鼓楼区五四路 88 号"},
                {"kind": "other", "label": "LinkedIn", "value": "linkedin.com/in/wanqing"},
            ],
        },
        {
            "name": "陈砚",
            "company": "南屿设计",
            "jobTitle": "设计总监",
            "tags": ["供应商"],
            "bookmarked": False,
            "notes": "品牌视觉供应商，合同 12 月到期。",
            "methods": [
                {"kind": "phone", "label": "", "value": "13900139002"},
                {"kind": "email", "label": "", "value": "chen.yan@example.com"},
            ],
        },
    ]
    workbook = Workbook()
    _write_sheet(workbook, examples)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer