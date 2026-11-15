"""Generate demo Excel files used for screenshots and for the blog."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from addressbook import create_app
from addressbook import repository as repo
from addressbook.excel_io import export_workbook, template_workbook

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sample_data"

IMPORT_CONTACTS = [
    {
        "name": "江月",
        "company": "云栖数据",
        "jobTitle": "数据分析师",
        "tags": ["客户"],
        "bookmarked": True,
        "notes": "新签约客户，11 月启动数据治理项目。",
        "methods": [
            {"kind": "phone", "label": "", "value": "186 0018 6001"},
            {"kind": "email", "label": "", "value": "jiangyue@example.com"},
            {"kind": "wechat", "label": "", "value": "jiangyue_data"},
        ],
    },
    {
        "name": "韩川",
        "company": "北辰咨询",
        "jobTitle": "合伙人",
        "tags": ["合作伙伴", "重点"],
        "bookmarked": False,
        "notes": "渠道合作，季度返点按合同执行。",
        "methods": [
            {"kind": "phone", "label": "工作", "value": "187 0018 7002"},
            {"kind": "phone", "label": "座机", "value": "0591-8888 6666"},
            {"kind": "email", "label": "", "value": "hanchuan@example.com"},
            {"kind": "wechat", "label": "", "value": "hanchuan_bc"},
            {"kind": "address", "label": "公司", "value": "福州市台江区江滨西大道 100 号"},
        ],
    },
    {
        "name": "林晚晴",
        "company": "星野科技",
        "jobTitle": "产品经理",
        "tags": ["客户"],
        "bookmarked": False,
        "notes": "与通讯录中已有联系人重复，用来演示查重。",
        "methods": [{"kind": "phone", "label": "", "value": "138 0013 8001"}],
    },
    {
        "name": "",
        "company": "缺少姓名示例",
        "jobTitle": "",
        "tags": [],
        "bookmarked": False,
        "notes": "",
        "methods": [{"kind": "phone", "label": "", "value": "185 0018 5000"}],
    },
    {
        "name": "陆遥",
        "company": "独立开发者",
        "jobTitle": "全栈工程师",
        "tags": ["朋友", "技术"],
        "bookmarked": True,
        "notes": "开源项目合作，偏好微信联系。",
        "methods": [
            {"kind": "phone", "label": "", "value": "188 0018 8004"},
            {"kind": "email", "label": "", "value": "luyao@example.com"},
            {"kind": "other", "label": "GitHub", "value": "github.com/luyao"},
        ],
    },
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    app = create_app()
    with app.app_context():
        contacts = repo.list_contacts()
        (OUT / "contacts-export-demo.xlsx").write_bytes(export_workbook(contacts).getvalue())
    (OUT / "import-demo.xlsx").write_bytes(export_workbook(IMPORT_CONTACTS).getvalue())
    (OUT / "import-template.xlsx").write_bytes(template_workbook().getvalue())
    print("written to", OUT)


if __name__ == "__main__":
    main()