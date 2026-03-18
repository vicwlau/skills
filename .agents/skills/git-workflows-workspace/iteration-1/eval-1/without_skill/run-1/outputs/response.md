# Using tailwindcss as a Starting Point

You can clone the repo and then delete the `.git` folder to remove the history and remote connections.

## Steps

**1. Clone the repository**

```powershell
git clone https://github.com/tailwindlabs/tailwindcss.git
cd tailwindcss
```

**2. Delete the `.git` folder**

In PowerShell on Windows:

```powershell
Remove-Item -Recurse -Force .git
```

This removes all the Git history and remote tracking information.

**3. Start fresh (optional)**

If you want to start tracking your own changes with Git, you can initialize a new repository:

```powershell
git init
git add .
git commit -m "Initial commit"
```

That's it! You now have all the Tailwind CSS source files without any of the original project's Git history or remote connections.
