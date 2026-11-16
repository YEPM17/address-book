"""Demo contacts used for screenshots and manual testing.

All people, companies, phone numbers and addresses below are fictional.
"""

from __future__ import annotations

from .repository import create_contact, stats

DEMO_CONTACTS = [
    {
        "name": "林晚晴",
        "company": "星野科技",
        "jobTitle": "产品经理",
        "tags": ["客户", "重点"],
        "bookmarked": True,
        "notes": "季度例会主持人，偏好邮件沟通；下次复盘约在 11 月 28 日。",
        "methods": [
            {"kind": "phone", "label": "工作", "value": "138 0013 8001"},
            {"kind": "phone", "label": "座机", "value": "0591-8800 1234"},
            {"kind": "email", "label": "", "value": "wanqing.lin@example.com"},
            {"kind": "wechat", "label": "", "value": "wanqing_l"},
            {"kind": "qq", "label": "", "value": "wanqing_im"},
            {"kind": "address", "label": "公司", "value": "福州市鼓楼区五四路 88 号星野大厦 12F"},
            {"kind": "other", "label": "LinkedIn", "value": "linkedin.com/in/wanqing-lin"},
        ],
    },
    {
        "name": "陈砚",
        "company": "南屿设计",
        "jobTitle": "设计总监",
        "tags": ["供应商"],
        "bookmarked": False,
        "notes": "品牌视觉供应商，年度合同 12 月到期，续约前需要比价。",
        "methods": [
            {"kind": "phone", "label": "", "value": "139 0013 9002"},
            {"kind": "email", "label": "", "value": "chen.yan@example.com"},
        ],
    },
    {
        "name": "周予安",
        "company": "远山资本",
        "jobTitle": "投资经理",
        "tags": ["投资人"],
        "bookmarked": True,
        "notes": "关注企业服务方向，BP 请先发邮箱。",
        "methods": [
            {"kind": "phone", "label": "", "value": "137 0013 7003"},
            {"kind": "email", "label": "", "value": "yuan.zhou@example.com"},
            {"kind": "wechat", "label": "", "value": "zhouyuan_vc"},
        ],
    },
    {
        "name": "苏禾",
        "company": "禾木文化",
        "jobTitle": "内容策划",
        "tags": ["合作伙伴"],
        "bookmarked": False,
        "notes": "联合直播项目对接人，周三下午方便沟通。",
        "methods": [
            {"kind": "phone", "label": "", "value": "136 0013 6004"},
            {"kind": "wechat", "label": "", "value": "suhe_studio"},
        ],
    },
    {
        "name": "顾承宇",
        "company": "云梯网络",
        "jobTitle": "技术总监",
        "tags": ["客户", "技术"],
        "bookmarked": False,
        "notes": "负责接口联调，偏好文字沟通，不接受临时电话。",
        "methods": [
            {"kind": "phone", "label": "", "value": "135 0013 5005"},
            {"kind": "email", "label": "工作", "value": "chengyu.gu@example.com"},
            {"kind": "qq", "label": "", "value": "tangyiran_im"},
        ],
    },
    {
        "name": "沈知微",
        "company": "青柠教育",
        "jobTitle": "创始人",
        "tags": ["客户"],
        "bookmarked": True,
        "notes": "重点客户，关注续费方案；公司地址在软件园 A 区。",
        "methods": [
            {"kind": "phone", "label": "", "value": "134 0013 4006"},
            {"kind": "email", "label": "", "value": "zhiwei.shen@example.com"},
            {"kind": "address", "label": "公司", "value": "福州市闽侯县上街镇软件园 A 区 6 号楼"},
        ],
    },
    {
        "name": "罗一舟",
        "company": "自由职业",
        "jobTitle": "摄影师",
        "tags": ["朋友"],
        "bookmarked": False,
        "notes": "产品拍摄长期合作，器材党，聊镜头会很开心。",
        "methods": [
            {"kind": "phone", "label": "", "value": "133 0013 3007"},
            {"kind": "wechat", "label": "", "value": "luoyizhou_photo"},
            {"kind": "other", "label": "Instagram", "value": "instagram.com/luoyizhou"},
        ],
    },
    {
        "name": "白露",
        "company": "城市大学",
        "jobTitle": "副教授",
        "tags": ["老师"],
        "bookmarked": False,
        "notes": "软件工程课程指导老师，邮件回复很快。",
        "methods": [
            {"kind": "phone", "label": "", "value": "132 0013 2008"},
            {"kind": "email", "label": "学校", "value": "bailu@example.edu.cn"},
            {"kind": "address", "label": "", "value": "福州市大学城学园路 2 号"},
        ],
    },
    {
        "name": "秦远",
        "company": "东岸物流",
        "jobTitle": "运营主管",
        "tags": ["供应商"],
        "bookmarked": False,
        "notes": "仓储与配送对接，月底对账。",
        "methods": [
            {"kind": "phone", "label": "", "value": "131 0013 1009"},
            {"kind": "qq", "label": "", "value": "qinyuan_im"},
        ],
    },
    {
        "name": "许棠",
        "company": "拾光书店",
        "jobTitle": "店长",
        "tags": ["朋友"],
        "bookmarked": True,
        "notes": "线下读书会场地合作，周末人多，建议提前一周预约。",
        "methods": [
            {"kind": "phone", "label": "", "value": "130 0013 0010"},
            {"kind": "wechat", "label": "", "value": "xutang_books"},
            {"kind": "address", "label": "书店", "value": "福州市仓山区烟台山乐群路 15 号"},
        ],
    },
    {
        "name": "唐亦然",
        "company": "峰岚咨询",
        "jobTitle": "高级顾问",
        "tags": ["合作伙伴"],
        "bookmarked": False,
        "notes": "组织架构咨询项目合作方，习惯用钉钉。",
        "methods": [
            {"kind": "email", "label": "", "value": "yiran.tang@example.com"},
            {"kind": "other", "label": "钉钉", "value": "tangyiran"},
        ],
    },
    {
        "name": "方既明",
        "company": "南风工作室",
        "jobTitle": "插画师",
        "tags": ["供应商"],
        "bookmarked": False,
        "notes": "插画外包，档期通常排到一个月后。",
        "methods": [
            {"kind": "wechat", "label": "", "value": "fangjiming_art"},
            {"kind": "other", "label": "Behance", "value": "behance.net/fangjiming"},
        ],
    },
    {
        "name": "江照",
        "company": "星野科技",
        "jobTitle": "人力资源经理",
        "tags": ["客户"],
        "bookmarked": False,
        "notes": "校招合作联系人，10 月宣讲会。",
        "methods": [
            {"kind": "phone", "label": "", "value": "188 0018 8011"},
            {"kind": "email", "label": "", "value": "zhao.jiang@example.com"},
        ],
    },
    {
        "name": "温故",
        "company": "旧雨咖啡馆",
        "jobTitle": "主理人",
        "tags": ["朋友"],
        "bookmarked": True,
        "notes": "常去的咖啡馆，二楼可以安静开会。",
        "methods": [
            {"kind": "phone", "label": "", "value": "189 0018 9012"},
            {"kind": "address", "label": "门店", "value": "福州市鼓楼区三坊七巷南后街 32 号"},
        ],
    },
]


def seed_demo_data() -> int:
    if stats()["total"] > 0:
        return 0
    for contact in DEMO_CONTACTS:
        create_contact(contact)
    return len(DEMO_CONTACTS)