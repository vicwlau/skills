---
name: git-workflows
description: Step-by-step guidance for common advanced Git workflows, including cloning a full repository and stripping its Git history, downloading only a specific sub-directory from a GitHub repo using degit, and feature branch development with a clean merge back to main. Use this skill whenever the user asks about cloning a repo, downloading part of a GitHub project, starting a feature branch, or merging a branch back to main — even if they don't use exact Git terminology.
---

# Git Workflows

A practical guide to three high-value Git workflows. Always detect the user's OS and tailor every command accordingly:
- **Windows** → PowerShell syntax
- **macOS / Linux** → Bash syntax

If the OS is ambiguous, ask before giving commands.

---

## Workflow 1 — Clone a Full Repo & Strip Its Git History

Use this when the user wants a clean copy of a repository to use as a starting point for their own project, without inheriting the original repo's commit history or remote connections.

### Why strip the history?
Keeping the original `.git` folder means:
- The project is still "owned" by the upstream remote
- Submodule references and remote hooks from the original can cause confusion
- The user can't push to their own remote cleanly

Removing `.git` gives them a blank slate.

### Steps

**1. Clone the repo (shallow, latest commit only)**

_Bash | PowerShell:_
```bash | powershell
git clone --depth 1 https://github.com/OWNER/REPO.git
cd REPO
```

> `--depth 1` fetches only the latest snapshot — much faster for large repos.

**2. Remove the original Git metadata**

```bash
rm -rf .git
```

```powershell
Remove-Item -Recurse -Force .git
```

**3. Check for leftover submodule references**

```bash | powershell
cat .gitmodules   # bash
Get-Content .gitmodules   # powershell
```

If `.gitmodules` exists, delete it too:
```bash | powershell
# If bash
rm -f .gitmodules

# If powershell 
Remove-Item -ErrorAction SilentlyContinue .gitmodules
```

**4. Initialize a fresh Git repo (optional but recommended)**

Ensure you're inside the repo directory (`REPO/`) before running these:

```bash | powershell
git init
git add .
git commit -m "chore: initial commit from OWNER/REPO template"
```

---

## Workflow 2 — Download a Specific Sub-directory with degit

Use this when the user only wants a folder inside a repo, not the whole thing. `degit` is the cleanest tool for this — it downloads just the files, no Git history, no `.git` folder.

### Prerequisites

`degit` is available via `bunx` (no install needed):

```bash | powershell
# No install needed (recommended):
bunx degit OWNER/REPO/path/to/subdir ./local-destination
```

> `bunx` is preferred because it requires no global install. If the user doesn't have `bun`, suggest `npx degit` as the fallback.

### Steps

**1. Run degit with the subdirectory path**

```bash | powershell
bunx degit OWNER/REPO/subdirectory ./my-folder
```

Replace `OWNER/REPO/subdirectory` with the actual GitHub path. For example:
```bash | powershell
bunx degit anthropics/skills/skills/skill-creator ./skill-creator
```

**2. Verify the download**

```bash | powershell
ls ./my-folder
```

### When degit won't work (private repos or branches)

For private repos or non-default branches, fall back to sparse checkout:

```bash | powershell
# 1. Partial clone (no file content, no history)
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/OWNER/REPO.git
cd REPO

# 2. Enable cone-mode sparse checkout (fastest)
git sparse-checkout init --cone

# 3. Specify the folder to materialize
git sparse-checkout set path/to/subdir

# 4. Check out
git checkout main   # or the target branch name

# 5. Strip Git history if you want a clean copy
cd ..
# bash:
rm -rf REPO/.git
# powershell:
Remove-Item -Recurse -Force REPO/.git
```

---

## Workflow 3 — Feature Branch Development & Merge to Main

Use this when the user wants to develop a new feature in isolation and then merge it back cleanly. This is the standard "feature branch" pattern.

### Why branch?
- Keeps `main` stable and deployable at all times
- Makes it easy to discard incomplete work without affecting others
- Enables clean pull request / code review workflows

### Steps

**1. Make sure you're on an up-to-date main**

```bash | powershell
git checkout main
git pull origin main
```

**2. Create and switch to your feature branch**

```bash | powershell
git checkout -b feat/your-feature-name
```

> Use a descriptive name like `feat/user-auth` or `fix/login-redirect`. The `feat/` prefix matches Conventional Commits guidelines.

**3. Do your work — commit often**

```bash | powershell
git add .
git commit -m "feat: describe what you did"
```

Good commit messages follow this pattern:
```
type: short summary (under 72 chars)

Optional longer explanation here.
```
Common types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`

**4. Stay in sync with main (while your branch is open)**

If main has moved on while you were working:

```bash | powershell
git fetch origin
git rebase origin/main
# or if you prefer merge over rebase:
git merge origin/main
```

`rebase` gives a cleaner linear history; `merge` preserves the full branch structure. For solo work, `rebase` is usually the right choice.

**5. Merge back to main when done**

```bash | powershell
git checkout main
git pull origin main          # make sure main is current
git merge feat/your-feature-name
git push origin main
```

If you want a merge commit (preserves branch history visually):
```bash | powershell
git merge --no-ff feat/your-feature-name
git push origin main
```

**6. Delete the feature branch (optional cleanup)**

```bash | powershell
git branch -d feat/your-feature-name        # local
git push origin --delete feat/your-feature-name  # remote
```

### Conflict resolution (if it comes up)

If `merge` or `rebase` hits a conflict:

```bash | powershell
# 1. See what's conflicting
git status

# 2. Open the conflicting files, look for <<<<<<< markers, resolve them

# 3. Stage the resolved files
git add path/to/resolved-file

# 4a. If you were merging:
git commit

# 4b. If you were rebasing:
git rebase --continue
```

---

## Quick Reference

| Goal | Command |
|---|---|
| Clone latest snapshot only | `git clone --depth 1 <url>` |
| Remove Git history (bash) | `rm -rf .git` |
| Remove Git history (PS) | `Remove-Item -Recurse -Force .git` |
| Download a subfolder | `bunx degit OWNER/REPO/subdir ./dest` |
| Create feature branch | `git checkout -b feat/name` |
| Sync with main | `git fetch origin && git rebase origin/main` |
| Merge feature to main | `git checkout main && git merge feat/name` |
| Delete branch (local) | `git branch -d feat/name` |
