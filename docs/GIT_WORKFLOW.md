# Git Workflow and Submission Checklist

This repository was prepared by **刘冉 (832401215)**. The workflow below is the
one used while building it, plus the exact commands needed to publish it on
GitHub. Some steps (fork, push, PR, release) must be repeated on GitHub with the
author's account.

## 1. Repository setup

```bash
# 1. Fork the assignment repository from the course organisation (GitHub UI).
# 2. Create the team repository named address-book (or use the fork).

git clone https://github.com/<username>/address-book.git
cd address-book
git config user.name  "刘冉"
git config user.email "<github-email>"
git config --get user.name
```

Recommended repository settings:

- protect `main`: require a pull request (self-review is acceptable for a solo
  submission);
- enable “Automatically delete head branches”;
- add a short description and topics (`flask`, `sqlite`, `address-book`, `excel`).

## 2. Day-to-day flow

```bash
git switch main && git pull
git switch -c feature/excel-import
# ... code, run tests ...
python -m unittest discover -s tests -v
git add -A
git commit -m "feat(import): preview Excel rows and flag duplicates"
git push -u origin feature/excel-import
```

Then open a pull request on GitHub, fill in
`.github/PULL_REQUEST_TEMPLATE.md`, review the diff against the checklist and
merge with “Create a merge commit” (so the PR is visible in the history).

Confirm the identity used before committing:

```bash
git config user.name
git config user.email
```

To fix an author on the last commit:

```bash
git commit --amend --author="刘冉 <github-email>" --no-edit
```

## 3. Release and submission

```bash
git switch main && git pull
git tag -a v1.0.0 -m "Folio v1.0.0: bookmarks, multiple methods, Excel import/export"
git push origin v1.0.0
```

On GitHub: **Releases → Draft a new release → choose v1.0.0**, attach a source
zip if required, and publish. Then submit the repository URL and the CSDN blog
link in the course channel.

## 4. Evidence for the blog

```bash
# Commit count
git shortlog -sne --all

# Graph used for the report
git log --graph --oneline --decorate --all

# Files changed per commit
git log --stat --oneline
```

Take a screenshot of the GitHub **Insights → Commits** page (or the commit list)
after pushing. A single author filter (`?author=<username>`) is enough for a
solo submission.

## 5. Preparing this local repository

The checkout already contains the full history authored by 刘冉 and a `v1.0.0`
tag. To publish it:

```bash
cd address-book

# 1. Point the remote at your repository
git remote remove origin 2>/dev/null
git remote add origin https://github.com/<username>/address-book.git

# 2. Push main, the feature branch and the tag
git push -u origin main
git push origin feature/contact-ui
git push origin v1.0.0
```

If the GitHub account uses a different e-mail than the one in the commits,
rewrite the author before pushing (this changes every hash; regenerate the
commit-history screenshot afterwards):

```bash
git filter-branch --env-filter '
export GIT_AUTHOR_NAME="刘冉"
export GIT_AUTHOR_EMAIL="<github-email>"
export GIT_COMMITTER_NAME="刘冉"
export GIT_COMMITTER_EMAIL="<github-email>"
' -- --all
```

If the assignment requires a pull request against the upstream fork, open it
from this repository's `main` into the upstream repository and paste the URL
into the blog.

## 6. Final checklist

- [ ] Repository is public (or the teaching staff has access).
- [ ] `main` contains at least three commits, all authored by 刘冉.
- [ ] `README.md`, `docs/CODE_STANDARDS.md`, `docs/PSP.md` are present.
- [ ] `v1.0.0` release exists and the pull request is merged/closed.
- [ ] The app starts from a clean clone (`run.bat` / `run.sh`).
- [ ] Blog contains all screenshots, the demo video, the PSP table and the
      contribution ratio (100%).
- [ ] Blog link submitted before **2026-11-17 23:59 (UTC+8)**.