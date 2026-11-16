# Code Standards — Folio Address Book

These rules are the standards followed in this project. They are intentionally
short enough to check in review and concrete enough to settle arguments.

## 1. Language and naming

| Thing | Rule | Example |
| --- | --- | --- |
| Python modules / packages | `snake_case` | `excel_io.py`, `repository.py` |
| Python functions / variables | `snake_case` | `list_contacts`, `is_bookmarked` |
| Python classes / exceptions | `PascalCase` | `ValidationError`, `ExcelImportError` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_METHODS`, `KIND_ORDER` |
| SQL tables / columns | `snake_case`, plural tables | `contacts`, `contact_methods`, `job_title` |
| JS functions / variables | `camelCase` | `renderContacts`, `selectedImportRows` |
| JS constants | `UPPER_SNAKE_CASE` | `KIND_META`, `PALETTES` |
| CSS classes | lowercase, hyphen-separated, component prefix | `contact-row`, `method-chip`, `modal-foot` |
| API JSON fields | `camelCase` | `jobTitle`, `isBookmarked` → `bookmarked` |
| Test files | `test_<module>.py` | `test_api.py` |

UI copy is Chinese; identifiers, comments, commit messages and docs are English.
No pinyin abbreviations (`lxr`, `dh`) and no single-letter names outside loops.

## 2. Python

- PEP 8, four spaces, 100-character soft limit, UTF-8, LF line endings.
- Type hints on public functions; `from __future__ import annotations` at the top.
- Docstrings on modules and non-trivial functions (what and why, not how).
- Imports in three groups: standard library, third-party, local. No wildcard
  imports.
- All SQL lives in `repository.py` / `db.py`; API handlers never build SQL.
- **Always parameterise SQL.** Never interpolate user input, even for `LIKE`
  patterns — use `_like_escape` plus `ESCAPE '\'`.
- Validate at the boundary (`validate_contact`) and return a clean dict; do not
  pass request JSON deeper into the app.
- Raise `ValidationError` for expected user mistakes; let unexpected errors
  bubble up and return 500. Do not catch `Exception` just to log it.
- Timestamps: UTC, ISO-8601, `strftime("%Y-%m-%dT%H:%M:%SZ")`.
- Commit after a logical change; keep functions under ~60 lines where practical.
- Formatting: `black -l 100` and `ruff check` are the reference tools. Neither
  is required at runtime, so the app stays installable with two packages.

## 3. JavaScript

- One strict IIFE, ES2020, no framework and no build step.
- `const` by default, `let` only when reassigned, never `var`.
- All user data goes through `esc()` or `textContent`; never concatenate raw
  contact values into `innerHTML`. This is the XSS boundary — review it on every
  change.
- Event delegation on containers for dynamic lists; do not attach a listener per
  row.
- API calls go through the single `api()` helper so errors and JSON parsing stay
  consistent.
- Keep state in one `state` object; rendering functions are pure with respect to
  that state (`renderContacts`, `renderDrawer`, …).
- Async functions must handle errors and surface a toast; no unhandled promise
  rejections.
- Accessibility: every icon-only button has `aria-label`, dialogs use
  `role="dialog"` + `aria-modal`, lists are keyboard reachable (`Enter`/`Space`).
- CSS uses custom properties from `:root`; no magic colours inside rules. All
  interactive states need `:hover` and `:focus-visible`.

## 4. Database

- Schema changes go into `SCHEMA` in `db.py` with `IF NOT EXISTS` so a fresh
  start is always safe.
- Foreign keys are enabled per connection; deleting a contact cascades to its
  methods.
- Add indexes for columns used by filtering (`name`, `is_bookmarked`,
  `contact_methods.contact_id`).
- Store tags wrapped in commas (`,a,b,`) to make exact tag matching cheap.
- Never store secrets or user files in the database.

## 5. HTTP / API

- JSON in, JSON out; UTF-8; `Content-Type: application/json`.
- Status codes: `200` read/update, `201` create, `400` validation, `404` missing,
  `413` upload too large, `500` unexpected.
- Error shape: `{"error": {"message": "...", "fields": {"field": "..."}}}`.
- File downloads set `Content-Disposition` with an ASCII filename.
- New endpoints need a test in `tests/test_api.py`.

## 6. Tests

- Every bug fix gets a regression test.
- Tests must not depend on network access or the developer's existing database:
  each case creates its own SQLite file under `tests/_work/`.
- Prefer asserting on behaviour (counts, statuses, parsed values) over exact HTML.
- Run before every commit:

  ```bash
  python -m unittest discover -s tests -v
  ```

- A pull request is not ready while any test fails.

## 7. Git

### Branches

| Branch | Purpose |
| --- | --- |
| `main` | always runnable; protected, only merged via PR |
| `feature/<short-name>` | a feature or fix |
| `docs/<short-name>` | documentation-only changes |

### Commit messages — Conventional Commits

```
<type>(optional scope): <imperative summary>

<optional body: why, trade-offs, linked issue>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`.

Examples:

```
feat(import): preview Excel rows and flag duplicates
fix(ui): keep bookmark filter in sync after unstarring
docs: add PSP tables and Git workflow
```

Rules:

- One logical change per commit; no “update files” commits.
- Summary ≤ 72 characters, imperative mood, no trailing period.
- Do not commit `.venv/`, `instance/`, `__pycache__/` or personal data.
- Never rewrite `main`; use revert commits.

### Pull requests

- Title mirrors the main commit; description uses `.github/PULL_REQUEST_TEMPLATE.md`.
- At least one peer review against the PR checklist; the reviewer merges (or
  the author merges after the reviewer approves).
- CI/manual test evidence (command + result) goes into the PR description.
- Delete the branch after merge.
- Tag releases `vMAJOR.MINOR.PATCH`; the tag message lists the delivered features.

## 8. Definition of done

A change is done when:

1. It works in the browser and the API, including the error path.
2. Tests pass and new behaviour is covered.
3. `README.md` / API docs are updated if the contract changed.
4. No debug `print`, no commented-out code, no secrets.
5. It is committed with a Conventional Commit message and merged through a PR.