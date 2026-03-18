# Evals for New Skill
- denied read access to certain folder
- use google for `moma.corp.google.com.md`; internal intranet search/wiki system
- subagents running into `503 capacity errors`

# Download a specific folder from a repo

```bash | powershell

# Modern way to download a specific folder from a repo
bunx degit anthropics/skills/skills/skill-creator ./skill-creator

# ---
# Alternative Way:
# ---

# 1. Partial clone: Downloads history/structure but NO file content (blobs)
# --depth 1: Only download the latest commit (not full history)
# url is the root of the repo
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/anthropics/skills.git
cd skills

# 2. Initialize modern sparse-checkout in "cone" mode (fastest)
git sparse-checkout init --cone

# 3. Define the specific directory to "materialize"
git sparse-checkout set skills/skill-creator

# 4. Pull the files for just that directory
git checkout main
```

# Remove hidden .git folder

```bash | powershell
rm -rf .git
```

# Check for submodules

```bash | powershell
git submodule status
```