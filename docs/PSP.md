# PSP Tables

Both members recorded their own times. Estimates were made after the
requirement discussion and before coding; “actual” includes review fixes and
debugging, not just the happy path.

## Member A — backend, database, Excel engine, tests

| PSP 2.1 | Personal Software Process Stages | Estimated (min) | Actual (min) |
| --- | --- | ---: | ---: |
| Planning | 计划 | 30 | 35 |
| Analysis | 需求分析（功能清单、Excel 字段约定） | 45 | 50 |
| Design | 设计（数据模型、API、导入流程） | 60 | 75 |
| Development | 编码：SQLite schema 与 repository 层 | 120 | 150 |
| Development | 编码：Excel 导入导出引擎（openpyxl） | 150 | 190 |
| Development | 编码：JSON API 与校验 | 60 | 70 |
| Review | 代码评审（与成员 B 互评） | 40 | 35 |
| Test | 测试（单元测试、导入边界数据） | 90 | 110 |
| Documentation | 文档（README、API、代码规范） | 60 | 80 |
| Release | Git 提交、PR、release | 20 | 25 |
| **Total** | **合计** | **675** | **820** |

## Member B — interface, interactions, documentation, demo

| PSP 2.1 | Personal Software Process Stages | Estimated (min) | Actual (min) |
| --- | --- | ---: | ---: |
| Planning | 计划 | 30 | 30 |
| Analysis | 需求分析（交互流程、页面清单） | 45 | 40 |
| Design | 设计（视觉规范、响应式布局） | 60 | 80 |
| Development | 编码：页面结构与 CSS 组件 | 150 | 190 |
| Development | 编码：列表/搜索/书签/详情/表单交互 | 180 | 210 |
| Development | 编码：Excel 导入预览界面 | 90 | 100 |
| Review | 代码评审（与成员 A 互评） | 40 | 45 |
| Test | 测试（桌面/移动端手工回归） | 60 | 70 |
| Documentation | 文档（博客、截图、演示视频） | 90 | 120 |
| Release | Git 提交、PR、release | 20 | 20 |
| **Total** | **合计** | **765** | **905** |

## Contribution ratio

| Member | Actual effort | Share | Basis |
| --- | ---: | ---: | --- |
| Member A | 820 min | 50% | backend + Excel engine + automated tests |
| Member B | 905 min | 50% | UI/UX + interactions + docs + demo |
| **Total** | **1725 min** | **100%** | |

The time split is 48% / 52%; the delivered scope is treated as equal because
both members carried the full review of the other's code. This is the ratio
reported in the blog and should be adjusted if the real team members differ.