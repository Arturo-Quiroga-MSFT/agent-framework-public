# ThoughtWorks Private Repo Sync Guide
https://github.com/Arturo-Quiroga-MSFT/thoughtworks-architecture

## Quick Start

Sync your latest ThoughtWorks materials to the private repo:

```bash
# From repository root
./sync_to_thoughtworks_private.sh
```

Or with a custom commit message:

```bash
./sync_to_thoughtworks_private.sh "Added Microsoft Foundry resources document"
```

## How It Works (rsync method)

The script uses **rsync** to sync files directly - this means:
- ✅ `AQ-THOUGHTWORKS-2026/` stays gitignored in public repo (clean!)
- ✅ Files sync to private repo without being tracked publicly
- ✅ No subtree complexity

**Flow:**
1. Clones/updates private repo to `/tmp/thoughtworks-private-sync`
2. Rsyncs `AQ-THOUGHTWORKS-2026/` contents (excluding `_local/`, `.DS_Store`)
3. Commits and pushes to private repo
4. Temp clone kept for faster subsequent syncs

## What It Does

1. ✅ Checks you're in the right directory
2. ✅ Prompts for commit message
3. ✅ Shows files to be synced
4. ✅ Clones/updates private repo
5. ✅ Rsyncs files (preserves .git)
6. ✅ Commits and pushes changes
7. ✅ Handles errors gracefully

## Usage Examples

### Basic Sync
```bash
./sync_to_thoughtworks_private.sh
```

### Sync After Making Changes
```bash
# Make your changes in AQ-THOUGHTWORKS-2026/
cd AQ-THOUGHTWORKS-2026
# Edit files...

# Sync (script will prompt for commit message)
cd ..
./sync_to_thoughtworks_private.sh "Added architecture documentation"
```

### Check What's in the Directory
```bash
# View ThoughtWorks files
ls -la AQ-THOUGHTWORKS-2026/
find AQ-THOUGHTWORKS-2026 -name "*.md"
```

## Workflow

### 1. Work in Public Repo
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public
cd AQ-THOUGHTWORKS-2026

# Make changes to ThoughtWorks materials
vim MICROSOFT_FOUNDRY_RESOURCES.md

# Files stay gitignored - never committed to public repo
```

### 2. Sync to Private Repo
```bash
# Return to root
cd ..

# Run sync script
./sync_to_thoughtworks_private.sh "Updated Foundry docs"
```

### 3. Team Members Pull Changes
```bash
# ThoughtWorks team can pull latest
cd thoughtworks-architecture
git pull origin main
```

## Troubleshooting

### Error: Must run from repository root

Ensure you're in the correct directory:
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public
```

### Clone Failed / Network Issues

Delete the temp clone and retry:
```bash
rm -rf /tmp/thoughtworks-private-sync
./sync_to_thoughtworks_private.sh
```

### No Changes to Commit

If you see "No changes to commit - already up to date", your local files match the private repo. Make changes first, then re-sync.

### Permission Denied

Ensure you have write access to the private repo:
```bash
# Test access
git ls-remote https://github.com/Arturo-Quiroga-MSFT/thoughtworks-architecture.git
```

## Advanced: Manual Sync

If the script doesn't work, sync manually:

```bash
# Clone private repo
rm -rf /tmp/thoughtworks-private-sync
git clone https://github.com/Arturo-Quiroga-MSFT/thoughtworks-architecture.git /tmp/thoughtworks-private-sync

# Rsync files (exclude .git!)
rsync -av --delete --exclude='.git/' --exclude='_local/' AQ-THOUGHTWORKS-2026/ /tmp/thoughtworks-private-sync/

# Commit and push
cd /tmp/thoughtworks-private-sync
git add -A
git commit -m "Manual sync"
git push origin main
```

## Configuration

Edit the script if you need to change:
- Repository paths
- Private repo URL
- Branch name
- Excluded files

```bash
# In sync_to_thoughtworks_private.sh
PUBLIC_REPO_DIR="/Users/arturoquiroga/GITHUB/agent-framework-public"
THOUGHTWORKS_DIR="AQ-THOUGHTWORKS-2026"
PRIVATE_REPO_URL="https://github.com/Arturo-Quiroga-MSFT/thoughtworks-architecture.git"
PRIVATE_CLONE_DIR="/tmp/thoughtworks-private-sync"
PRIVATE_BRANCH="main"
```

## Team Collaboration

Once synced, team members can:

```bash
# Clone private repo (first time)
git clone git@github.com:Arturo-Quiroga-MSFT/thoughtworks-architecture.git

# Pull latest changes
git pull origin main

# Make changes and push back
git add .
git commit -m "Added feedback on architecture"
git push origin main
```

You can then pull their changes into your public repo if needed:

```bash
# In public repo
cd AQ-THOUGHTWORKS-2026
git pull ../path/to/thoughtworks-architecture main
cd ..
# Note: Files stay gitignored, no accidental commits
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `./sync_to_thoughtworks_private.sh` | Sync changes to private repo |
| `./sync_to_thoughtworks_private.sh "message"` | Sync with custom commit message |
| `rm -rf /tmp/thoughtworks-private-sync` | Clear temp clone (for fresh start) |
| `ls AQ-THOUGHTWORKS-2026/` | View local ThoughtWorks files |
| `find AQ-THOUGHTWORKS-2026 -name "*.md"` | List all markdown files |

## Private Repo URL

https://github.com/Arturo-Quiroga-MSFT/thoughtworks-architecture

---

## Setup Instructions (One-Time)

### 1. Create Private GitHub Repo

Go to https://github.com/new and create:
- **Name:** `thoughtworks-architecture`
- **Visibility:** Private
- **Owner:** Arturo-Quiroga-MSFT
- **Description:** ThoughtWorks Architecture and Design Materials
- **Initialize:** With README (optional)

### 2. Make Script Executable

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public
chmod +x sync_to_thoughtworks_private.sh
```

### 3. Test Sync

```bash
./sync_to_thoughtworks_private.sh "Initial sync"
```

### 4. Verify

Check the private repo: https://github.com/Arturo-Quiroga-MSFT/thoughtworks-architecture

---

**Questions?** The script provides helpful error messages and confirmation prompts.
