import io
import shutil
import unittest
import uuid
from pathlib import Path

from openpyxl import Workbook

from addressbook import create_app
from addressbook.excel_io import (
    ExcelImportError,
    export_workbook,
    parse_workbook,
    template_workbook,
)


def make_workbook(headers, rows, title="Contacts"):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = title
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


class ExcelRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.workdir = Path(__file__).resolve().parent / "_work" / uuid.uuid4().hex
        self.workdir.mkdir(parents=True)
        self.app = create_app(
            {"TESTING": True, "DATABASE": str(self.workdir / "test.sqlite3")}
        )
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()
        shutil.rmtree(self.workdir, ignore_errors=True)

    def sample_contacts(self):
        return [
            {
                "name": "林晚晴",
                "company": "星野科技",
                "jobTitle": "产品经理",
                "tags": ["客户", "重点"],
                "bookmarked": True,
                "notes": "季度例会主持人",
                "methods": [
                    {"kind": "phone", "label": "工作", "value": "13800138001"},
                    {"kind": "phone", "label": "座机", "value": "0591-88001234"},
                    {"kind": "phone", "label": "", "value": "13800138002"},
                    {"kind": "email", "label": "", "value": "wanqing@example.com"},
                    {"kind": "email", "label": "备用", "value": "wanqing2@example.com"},
                    {"kind": "wechat", "label": "", "value": "wanqing_l"},
                    {"kind": "qq", "label": "", "value": "100200300"},
                    {"kind": "address", "label": "公司", "value": "福州市鼓楼区五四路 88 号"},
                    {"kind": "other", "label": "LinkedIn", "value": "linkedin.com/in/wanqing"},
                    {"kind": "other", "label": "GitHub", "value": "github.com/wanqing"},
                ],
            },
            {
                "name": "陈砚",
                "company": "南屿设计",
                "jobTitle": "设计总监",
                "tags": ["供应商"],
                "bookmarked": False,
                "notes": "",
                "methods": [{"kind": "phone", "label": "", "value": "13900139002"}],
            },
        ]

    def test_export_then_import_round_trip(self):
        buffer = export_workbook(self.sample_contacts())
        parsed = parse_workbook(buffer, "roundtrip.xlsx")

        self.assertEqual(parsed["summary"]["total"], 2)
        self.assertEqual(parsed["summary"]["ready"], 2)
        first = parsed["rows"][0]["contact"]
        self.assertEqual(first["name"], "林晚晴")
        self.assertTrue(first["bookmarked"])
        self.assertEqual(first["tags"], ["客户", "重点"])
        self.assertEqual(len(first["methods"]), 10)
        kinds = [method["kind"] for method in first["methods"]]
        self.assertEqual(kinds.count("phone"), 3)
        self.assertEqual(kinds.count("email"), 2)
        self.assertEqual(kinds.count("other"), 2)
        others = {method["label"]: method["value"] for method in first["methods"] if method["kind"] == "other"}
        self.assertEqual(others["GitHub"], "github.com/wanqing")

    def test_multiple_values_in_one_cell_are_split(self):
        buffer = make_workbook(
            ["Name", "Phone 1", "Email 1"],
            [["多值测试", "13800138001; 13900139002", "a@example.com；b@example.com"]],
        )
        parsed = parse_workbook(buffer, "multi.xlsx")
        contact = parsed["rows"][0]["contact"]
        phones = [method["value"] for method in contact["methods"] if method["kind"] == "phone"]
        emails = [method["value"] for method in contact["methods"] if method["kind"] == "email"]
        self.assertEqual(phones, ["13800138001", "13900139002"])
        self.assertEqual(emails, ["a@example.com", "b@example.com"])

    def test_headers_can_be_reordered_with_extra_columns(self):
        buffer = make_workbook(
            ["备注", "手机号 2", "Email", "Name", "Department", "手机号 1"],
            [["老客户", "13900139002", "a@example.com", "乱序表头", "研发部", "13800138001"]],
        )
        parsed = parse_workbook(buffer, "reordered.xlsx")
        contact = parsed["rows"][0]["contact"]
        self.assertEqual(contact["name"], "乱序表头")
        self.assertEqual(contact["notes"], "老客户")
        self.assertEqual(len(contact["methods"]), 3)

    def test_missing_name_is_reported(self):
        buffer = make_workbook(["Name", "Phone 1"], [["", "13800138001"]])
        parsed = parse_workbook(buffer, "missing.xlsx")
        self.assertEqual(parsed["rows"][0]["status"], "error")
        self.assertIn("缺少姓名", parsed["rows"][0]["messages"])

    def test_unknown_workbook_is_rejected(self):
        buffer = make_workbook(["Foo", "Bar"], [["x", "y"]])
        with self.assertRaises(ExcelImportError):
            parse_workbook(buffer, "unknown.xlsx")

    def test_empty_sheet_is_rejected(self):
        buffer = make_workbook(["Name", "Phone 1"], [])
        with self.assertRaises(ExcelImportError):
            parse_workbook(buffer, "empty.xlsx")

    def test_template_is_valid_and_non_empty(self):
        buffer = template_workbook()
        parsed = parse_workbook(buffer, "template.xlsx")
        self.assertEqual(parsed["summary"]["total"], 2)
        self.assertEqual(parsed["summary"]["ready"], 2)


if __name__ == "__main__":
    unittest.main()