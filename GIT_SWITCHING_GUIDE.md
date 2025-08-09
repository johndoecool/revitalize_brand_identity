# Git Repository Switching Guide

## Remote Configuration

- **github**: `git@github.com:johndoecool/revitalize_brand_identity.git`
- **ado**: `git@ssh.dev.azure.com:v3/Vibects13/118797/118797`

## Common Commands

### Pull from repositories

```bash
git pull github master    # Pull from GitHub
git pull ado master       # Pull from Azure DevOps
```

### Push to repositories

```bash
git push github master    # Push to GitHub
git push ado master       # Push to Azure DevOps
```

### Check current branch status against remotes

```bash
git status                        # Current branch status
git log --oneline github/master   # GitHub commits
git log --oneline ado/master      # Azure DevOps commits
```

### Sync between repositories

```bash
# To sync GitHub → Azure DevOps
git pull github master
git push ado master

# To sync Azure DevOps → GitHub
git pull ado master
git push github master
```

### View remote configuration

```bash
git remote -v    # Show all remotes
```

### Temporarily set default remote

```bash
git branch --set-upstream-to=github/master master    # Set GitHub as upstream
git branch --set-upstream-to=ado/master master       # Set ADO as upstream
```

## Quick Reference

- Use `github` for external collaboration
- Use `ado` for internal/enterprise workflows
- Always specify the remote name to avoid confusion
- Both remotes point to the same codebase but may have different commit histories

## Quick commands:

- git pull github master # Pull from GitHub
- git pull ado master # Pull from Azure DevOps
- git push github master # Push to GitHub
- git push ado master # Push to Azure DevOps
