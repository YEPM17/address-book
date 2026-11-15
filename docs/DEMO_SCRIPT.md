# Demo Video Script

Target length: **2–3 minutes**, 1080p or 1440×900, recorded with OBS Studio
(display capture) or Windows Game Bar (`Win + Alt + R`). Record the browser at
100% zoom, close unrelated tabs, and use the seeded demo data.

## Before recording

```bash
run.bat
.venv\Scripts\python -m flask --app app seed-demo   # only the first time
```

Open <http://127.0.0.1:5000>, press `F11` for full screen, and check the app
shows 14 contacts / 5 bookmarks.

## Shot list

| # | Time | Action | Narration (Chinese) |
| --- | --- | --- | --- |
| 1 | 0:00–0:12 | Start on the contact list; move the mouse across the header. | “这是 Folio 通讯录，支持书签、多条联系方式，以及 Excel 导入导出。” |
| 2 | 0:12–0:28 | Click **书签** in the sidebar, then **全部联系人**. | “侧边栏可以只看书签；书签联系人会自动排在最前面。” |
| 3 | 0:28–0:40 | Click the star on 陈砚, then show the count change; click 书签. | “点一下星标即可收藏或取消，书签数量实时更新。” |
| 4 | 0:40–1:05 | Open 林晚晴 → scroll the detail drawer. | “详情页展示电话、邮箱、微信、QQ、地址和自定义方式，每条都能一键复制。” |
| 5 | 1:05–1:30 | Click **编辑**; point at the method rows; add one method (e.g. 邮箱), fill a value, save. | “同一个联系人可以有多条电话和邮箱；这里新增一条联系方式并保存。” |
| 6 | 1:30–1:45 | Click **新建联系人**, fill name/company/phone, switch on 书签, create. | “新建时可以一次录入多种联系方式，并直接加入书签。” |
| 7 | 1:45–2:15 | Click **导入 Excel** → choose `sample_data/import-demo.xlsx`; show preview statuses. | “导入前会先预览：绿色可导入，黄色是重复联系人，红色是缺少姓名。” |
| 8 | 2:15–2:25 | Click **导入 3 位联系人**; show toast and new rows. | “确认后只写入无重复、校验通过的数据。” |
| 9 | 2:25–2:40 | Click **导出**; open the downloaded file in Excel (optional). | “导出的 Excel 一行一位联系人，每类信息都有独立列，并附带格式说明页。” |
| 10 | 2:40–2:50 | Toggle card view, then narrow the window to show mobile layout. | “列表和卡片两种视图，手机宽度下也能正常使用。” |
| 11 | 2:50–3:00 | End card: repository URL / author name. | “项目地址见博客，谢谢观看。” |

## Recording tips

- Do two takes: one for the happy path, one for a mistake (empty name shows the
  inline error) — keeping the error in the final cut proves validation works.
- Keep the mouse still while speaking; use the keyboard shortcut `/` to focus
  search, and `Esc` to close dialogs.
- Export the file as **MP4 / H.264**, under 200 MB, and upload it to Bilibili,
  YouTube (unlisted) or the course platform. Put the link in the blog; do not
  commit the video to Git.
- Mention the GitHub repository URL in the video description as well.

## Files used

- `sample_data/import-demo.xlsx` — 5 rows: 3 ready, 1 duplicate, 1 error.
- `sample_data/contacts-export-demo.xlsx` — an export of the demo book.
- `sample_data/import-template.xlsx` — blank template.