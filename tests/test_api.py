import io
import os
import shutil
import unittest
import uuid
from pathlib import Path

from openpyxl import Workbook, load_workbook

from addressbook import create_app


def workbook_bytes(headers, rows, sheet_title="Contacts"):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        # A plain mkdir under tests/ is used instead of tempfile: the CI-less
        # classroom Windows image sometimes blocks SQLite inside %TEMP% paths.
        self.workdir = Path(__file__).resolve().parent / "_work" / uuid.uuid4().hex
        self.workdir.mkdir(parents=True)
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(self.workdir / "test.sqlite3"),
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.workdir, ignore_errors=True)

    def create(self, payload):
        response = self.client.post("/api/contacts", json=payload)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        return response.get_json()["contact"]

    def test_index_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Folio", response.get_data(as_text=True))

    def test_create_list_and_search(self):
        contact = self.create(
            {
                "name": "林晚晴",
                "company": "星野科技",
                "jobTitle": "产品经理",
                "tags": "客户, 重点",
                "bookmarked": True,
                "notes": "季度例会",
                "methods": [
                    {"kind": "phone", "value": "13800138001"},
                    {"kind": "email", "value": "wanqing@example.com"},
                ],
            }
        )
        self.assertEqual(contact["name"], "林晚晴")
        self.assertTrue(contact["bookmarked"])
        self.assertEqual([method["kind"] for method in contact["methods"]], ["phone", "email"])

        listing = self.client.get("/api/contacts").get_json()
        self.assertEqual(listing["count"], 1)

        self.assertEqual(self.client.get("/api/contacts?q=星野").get_json()["count"], 1)
        self.assertEqual(self.client.get("/api/contacts?q=13800138001").get_json()["count"], 1)
        self.assertEqual(self.client.get("/api/contacts?q=重点").get_json()["count"], 1)
        self.assertEqual(self.client.get("/api/contacts?q=不存在").get_json()["count"], 0)

    def test_name_is_required(self):
        response = self.client.post("/api/contacts", json={"name": "  ", "methods": []})
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.get_json()["error"]["fields"])

    def test_multiple_contact_methods_are_preserved(self):
        contact = self.create(
            {
                "name": "陈砚",
                "methods": [
                    {"kind": "phone", "label": "工作", "value": "13900139002"},
                    {"kind": "phone", "label": "座机", "value": "0591-88001234"},
                    {"kind": "email", "value": "chen.yan@example.com"},
                    {"kind": "wechat", "value": "chenyan"},
                    {"kind": "qq", "value": "100200300"},
                    {"kind": "address", "label": "公司", "value": "福州市鼓楼区五四路 88 号"},
                    {"kind": "other", "label": "LinkedIn", "value": "linkedin.com/in/chenyan"},
                ],
            }
        )
        self.assertEqual(len(contact["methods"]), 7)
        self.assertEqual(contact["methods"][3]["value"], "chenyan")
        self.assertEqual(contact["methods"][6]["label"], "LinkedIn")

    def test_duplicate_methods_are_collapsed(self):
        contact = self.create(
            {
                "name": "重复方式",
                "methods": [
                    {"kind": "phone", "value": "13800138001"},
                    {"kind": "phone", "value": "13800138001"},
                ],
            }
        )
        self.assertEqual(len(contact["methods"]), 1)

    def test_bookmark_toggle_and_filter(self):
        contact = self.create({"name": "周予安", "methods": []})
        self.assertFalse(contact["bookmarked"])

        toggled = self.client.patch(f"/api/contacts/{contact['id']}/bookmark", json={})
        self.assertTrue(toggled.get_json()["bookmarked"])
        self.assertEqual(self.client.get("/api/contacts?bookmarked=1").get_json()["count"], 1)

        self.client.patch(f"/api/contacts/{contact['id']}/bookmark", json={"bookmarked": False})
        self.assertEqual(self.client.get("/api/contacts?bookmarked=1").get_json()["count"], 0)

    def test_update_replaces_methods(self):
        contact = self.create(
            {
                "name": "苏禾",
                "methods": [{"kind": "phone", "value": "13600136004"}],
            }
        )
        response = self.client.put(
            f"/api/contacts/{contact['id']}",
            json={
                "name": "苏禾",
                "company": "禾木文化",
                "methods": [
                    {"kind": "email", "value": "suhe@example.com"},
                    {"kind": "wechat", "value": "suhe_studio"},
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()["contact"]
        self.assertEqual(updated["company"], "禾木文化")
        self.assertEqual([method["kind"] for method in updated["methods"]], ["email", "wechat"])

    def test_delete_contact(self):
        contact = self.create({"name": "待删除", "methods": []})
        self.assertEqual(self.client.delete(f"/api/contacts/{contact['id']}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/contacts/{contact['id']}").status_code, 404)

    def test_meta_counts_tags(self):
        self.create({"name": "甲", "tags": ["客户", "重点"], "methods": []})
        self.create({"name": "乙", "tags": ["客户"], "methods": []})
        meta = self.client.get("/api/meta").get_json()
        self.assertEqual(meta["stats"]["total"], 2)
        self.assertEqual(meta["stats"]["methods"], 0)
        tags = {tag["name"]: tag["count"] for tag in meta["tags"]}
        self.assertEqual(tags["客户"], 2)

    def test_export_contains_labelled_columns(self):
        self.create(
            {
                "name": "导出一号",
                "company": "远山资本",
                "tags": ["投资人"],
                "bookmarked": True,
                "methods": [
                    {"kind": "phone", "value": "13700137003"},
                    {"kind": "phone", "value": "13700137004"},
                    {"kind": "email", "value": "one@example.com"},
                    {"kind": "other", "label": "LinkedIn", "value": "linkedin.com/in/one"},
                ],
            }
        )
        response = self.client.get("/api/export")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "spreadsheetml",
            response.headers["Content-Type"],
        )
        workbook = load_workbook(io.BytesIO(response.data))
        sheet = workbook["Contacts"]
        headers = [cell.value for cell in sheet[1]]
        self.assertIn("Name", headers)
        self.assertIn("Phone 1", headers)
        self.assertIn("Phone 2", headers)
        self.assertIn("Email 1", headers)
        self.assertIn("Other 1 Type", headers)
        self.assertIn("Bookmarked", headers)
        row = {headers[index]: cell.value for index, cell in enumerate(sheet[2])}
        self.assertEqual(row["Name"], "导出一号")
        self.assertEqual(row["Bookmarked"], "Yes")
        self.assertEqual(row["Phone 2"], "13700137004")
        self.assertIn("Read Me", workbook.sheetnames)

    def test_export_empty_is_rejected(self):
        self.assertEqual(self.client.get("/api/export").status_code, 400)

    def test_import_preview_and_commit(self):
        payload = workbook_bytes(
            ["Name", "Company", "Phone 1", "Phone 2", "Email 1", "Bookmarked", "Tags"],
            [
                ["白露", "城市大学", "13200132008", "0591-1234567", "bailu@example.edu.cn", "Yes", "老师, 学校"],
                ["", "缺少姓名", "13000000000", "", "", "No", ""],
            ],
        )
        response = self.client.post(
            "/api/import/preview",
            data={"file": (payload, "contacts.xlsx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        preview = response.get_json()
        self.assertEqual(preview["summary"]["total"], 2)
        self.assertEqual(preview["summary"]["ready"], 1)
        self.assertEqual(preview["summary"]["errors"], 1)

        ready = [row for row in preview["rows"] if row["status"] == "ok"]
        commit = self.client.post(
            "/api/import",
            json={"rows": [{"contact": row["contact"], "selected": True} for row in ready]},
        )
        self.assertEqual(commit.status_code, 200)
        self.assertEqual(commit.get_json()["imported"], 1)
        self.assertEqual(self.client.get("/api/contacts").get_json()["count"], 1)

    def test_import_duplicate_is_skipped(self):
        self.create(
            {
                "name": "顾承宇",
                "methods": [{"kind": "phone", "value": "13500135005"}],
            }
        )
        payload = workbook_bytes(
            ["Name", "Phone 1"],
            [["顾承宇", "13500135005"], ["新朋友", "13500139999"]],
        )
        preview = self.client.post(
            "/api/import/preview",
            data={"file": (payload, "dup.xlsx")},
            content_type="multipart/form-data",
        ).get_json()
        self.assertEqual(preview["summary"]["duplicates"], 1)
        self.assertEqual(preview["summary"]["ready"], 1)

        commit = self.client.post(
            "/api/import",
            json={
                "rows": [
                    {"contact": preview["rows"][0]["contact"]},
                    {"contact": preview["rows"][1]["contact"]},
                ]
            },
        ).get_json()
        self.assertEqual(commit["imported"], 1)
        self.assertEqual(commit["skipped"], 1)

    def test_import_accepts_chinese_headers(self):
        payload = workbook_bytes(
            ["姓名", "公司", "电话 1", "电话 2", "邮箱", "书签", "标签"],
            [["许棠", "拾光书店", "13000130010", "13000130011", "xutang@example.com", "是", "朋友"]],
        )
        preview = self.client.post(
            "/api/import/preview",
            data={"file": (payload, "cn.xlsx")},
            content_type="multipart/form-data",
        ).get_json()
        self.assertEqual(preview["summary"]["ready"], 1)
        contact = preview["rows"][0]["contact"]
        self.assertEqual(contact["name"], "许棠")
        self.assertTrue(contact["bookmarked"])
        self.assertEqual(len(contact["methods"]), 3)

    def test_import_rejects_non_excel(self):
        response = self.client.post(
            "/api/import/preview",
            data={"file": (io.BytesIO(b"not excel"), "notes.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_template_download(self):
        response = self.client.get("/api/import/template")
        self.assertEqual(response.status_code, 200)
        workbook = load_workbook(io.BytesIO(response.data))
        self.assertIn("Contacts", workbook.sheetnames)
        self.assertIn("Read Me", workbook.sheetnames)
        headers = [cell.value for cell in workbook["Contacts"][1]]
        self.assertIn("Phone 1", headers)
        self.assertIn("Other 1 Value", headers)

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()