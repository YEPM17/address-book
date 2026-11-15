# Git Workflow and Submission Checklist

This is the workflow the team agreed on before writing code, plus the exact
commands used to prepare the local repository. Some steps (fork, push, PR,
release) must be repeated on GitHub with your own accounts.

## 1. Repository setup

```bash
# 1. Fork the assignment repository from the course organisation (GitHub UI).
# 2. Create the team repository (or use the fork) and add the teammate:
#    Settings → Collaborators → Add people.

git clone https://github.com/<team>/address-book.git
cd address-book
git config user.name  "Member A"
git config user.email "member.a@example.com"
git config --get user.name
```

Recommended repository settings:

- protect `main`: require a pull request and one approving review;
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
`.github/PULL_REQUEST_TEMPLATE.md`, ask the teammate to review, and merge with
“Create a merge commit” (so the PR is visible in the history).

Each member must author commits. Before committing, confirm the identity used:

```bash
git config user.name
git config user.email
```

To fix an author on the last commit:

```bash
git commit --amend --author="Real Name <real@email>" --no-edit
```

## 3. Release and submission

```bash
git switch main && git pull
git tag -a v1.0.0 -m "Folio v1.0.0: bookmarks, multiple methods, Excel import/export"
git push origin v1.0.0
```

On GitHub: **Releases → Draft a new release → choose v1.0.0**, attach a source
zip if required, and publish. Then submit the repository URL and your CSDN blog
link in the course channel.

## 4. Evidence for the blog

```bash
# Commit count per author
git shortlog -sne --all

# Graph used for the report
git log --graph --oneline --decorate --all

# Files changed per commit
git log --stat --oneline
```

Take a screenshot of the GitHub **Insights → Commits** page (or the commit list)
and of each member's filtered commit list (`?author=<username>`).

## 5. Preparing this local repository

The checkout already contains a linear history with two authors and a release
tag. To publish it under your own accounts:

```bash
cd address-book

# 1. Point the remote at your team repository
git remote remove origin 2>/dev/null
git remote add origin https://github.com/<team>/address-book.git

# 2. Optional: rewrite the placeholder authors to the real members
#    (this changes every hash; do it before pushing)
git filter-branch --env-filter '
if [ "$GIT_AUTHOR_NAME" = "Member A" ]; then
  export GIT_AUTHOR_NAME="Real Name A"; export GIT_AUTHOR_EMAIL="a@example.com"
  export GIT_COMMITTER_NAME="Real Name A"; export GIT_COMMITTER_EMAIL="a@example.com"
fi
if [ "$GIT_AUTHOR_NAME" = "Member B" ]; then
  export GIT_AUTHOR_NAME="Real Name B"; export GIT_AUTHOR_EMAIL="b@example.com"
  export GIT_COMMITTER_NAME="Real Name B"; export GIT_COMMITTER_EMAIL="b@example.com"
fi' -- --all

# 3. Push main, the feature branch and the tag
git push -u origin main
git push origin feature/excel-import
git push origin v1.0.0
```

If the assignment requires a pull request against the upstream fork, open it
from the team repository's `main` into the upstream repository and paste the
URL into the blog.

## 6. Final checklist

- [ ] Repository is public (or the teaching staff has access).
- [ ] `main` contains at least three commits; both members authored commits.
- [ ] `README.md`, `docs/CODE_STANDARDS.md`, `docs/PSP.md` are present.
- [ ] `v1.0.0` release exists and the pull request is merged/closed.
- [ ] The app starts from a clean clone (`run.bat` / `run.sh`).
- [ ] Blog contains all screenshots, the demo video, PSP tables and the
      contribution ratio.
- [ ] Blog link submitted before **2026-11-17 23:59 (UTC+8)**.