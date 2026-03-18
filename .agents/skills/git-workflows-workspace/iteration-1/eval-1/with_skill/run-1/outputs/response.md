# Cloning tailwindcss as a Clean Starting Point (Windows)

Great idea — here's how to grab the Tailwind CSS repo and strip it down to a blank slate for your own project. Since you're on Windows, all commands use PowerShell.

---

## Step 1 — Clone the repo (latest snapshot only)

```powershell
git clone --depth 1 https://github.com/tailwindlabs/tailwindcss.git
cd tailwindcss
```

> `--depth 1` fetches only the most recent commit, not the full history. For a large repo like Tailwind this makes the clone **significantly faster**.

---

## Step 2 — Remove the original Git metadata

This severs all ties to the upstream remote and wipes the commit history:

```powershell
Remove-Item -Recurse -Force .git
```

---

## Step 3 — Check for leftover submodule references

Tailwind CSS doesn't use submodules, but it's good practice to check:

```powershell
Get-Content .gitmodules
```

If the file exists and has content, remove it too:

```powershell
Remove-Item -ErrorAction SilentlyContinue .gitmodules
```

---

## Step 4 — Initialize a fresh Git repo (recommended)

Now you have a clean folder. Start your own Git history:

```powershell
git init
git add .
git commit -m "chore: initial commit from tailwindlabs/tailwindcss template"
```

---

You now have a local copy of Tailwind CSS with no connection to the original repo — no remotes, no history, ready to be pushed to your own repository whenever you're ready.
