# Zafin Private Repo Sync Guide
https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture

## Quick Start

Sync your latest Zafin materials to the private repo:

```bash
# From repository root
./sync_to_zafin_private.sh
```

Or with a custom commit message:

```bash
./sync_to_zafin_private.sh "Updated persona-based observability framework"
```

## How It Works (rsync method)

The script uses **rsync** to sync files directly - this means:
- ✅ `AQ-ZAFIN-2026/` stays gitignored in public repo (clean!)
- ✅ Files sync to private repo without being tracked publicly
- ✅ No subtree complexity

**Flow:**
1. Clones/updates private repo to `/tmp/zafin-private-sync`
2. Rsyncs `AQ-ZAFIN-2026/` contents (excluding `_local/`, `.DS_Store`)
3. Commits and pushes to private repo
4. Temp clone kept for faster subsequent syncs

## What Gets Synced

| Content | Description |
|---------|-------------|
| `PERSONA_BASED_OBSERVABILITY_FRAMEWORK.md` | Framework for persona-specific observability |
| `PERSONA_BASED_OBSERVABILITY_FRAMEWORK*.docx` | Word versions for sharing |
| `SRE-AGENT-REFERENCE.md` | SRE Agent documentation |
| `ZAFIN-TECHNICAL-CHALLENGES.md` | Technical challenges and solutions |
| `sre-agent-main/` | Full SRE Agent samples and Bicep deployments |
| `From_Richard_Liang/` | Roadmap documents from Zafin |

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
./sync_to_zafin_private.sh
```

### Sync After Making Changes
```bash
# Make your changes in AQ-ZAFIN-2026/
cd AQ-ZAFIN-2026
# Edit files...

# Sync (script will prompt for commit message)
cd ..
./sync_to_zafin_private.sh "Added IaC patterns for AI Foundry"
```

### Check What's in the Directory
```bash
# View Zafin files
ls -la AQ-ZAFIN-2026/
find AQ-ZAFIN-2026 -name "*.md"
```

## Workflow

### 1. Work in Public Repo
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public
cd AQ-ZAFIN-2026

# Make changes to Zafin materials
vim PERSONA_BASED_OBSERVABILITY_FRAMEWORK.md

# Files stay gitignored - never committed to public repo
```

### 2. Sync to Private Repo
```bash
# Return to root
cd ..

# Run sync script
./sync_to_zafin_private.sh "Updated observability docs"
```

### 3. Team Members Pull Changes
```bash
# Zafin team can pull latest
cd zafin-multi-agent-architecture
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
rm -rf /tmp/zafin-private-sync
./sync_to_zafin_private.sh
```

### No Changes to Commit

If you see "No changes to commit - already up to date", your local files match the private repo. Make changes first, then re-sync.

### Permission Denied

Ensure you have write access to the private repo:
```bash
# Test access
git ls-remote https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture.git
```

## Advanced: Manual Sync

If the script doesn't work, sync manually:

```bash
# Clone private repo
rm -rf /tmp/zafin-private-sync
git clone https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture.git /tmp/zafin-private-sync

# Rsync files (exclude .git!)
rsync -av --delete --exclude='.git/' --exclude='_local/' AQ-ZAFIN-2026/ /tmp/zafin-private-sync/

# Commit and push
cd /tmp/zafin-private-sync
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
# In sync_to_zafin_private.sh
PUBLIC_REPO_DIR="/Users/arturoquiroga/GITHUB/agent-framework-public"
ZAFIN_DIR="AQ-ZAFIN-2026"
PRIVATE_REPO_URL="https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture.git"
PRIVATE_CLONE_DIR="/tmp/zafin-private-sync"
PRIVATE_BRANCH="main"
```

## Team Collaboration

Once synced, team members can:

```bash
# Clone private repo (first time)
git clone git@github.com:Arturo-Quiroga-MSFT/zafin-multi-agent-architecture.git

# Pull latest changes
git pull origin main

# Make changes and push back
git add .
git commit -m "Added feedback on observability"
git push origin main
```

You can then pull their changes into your public repo if needed:

```bash
# In public repo
cd AQ-ZAFIN-2026
git pull ../path/to/zafin-multi-agent-architecture main
cd ..
# Note: Files stay gitignored, no accidental commits
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `./sync_to_zafin_private.sh` | Sync changes to private repo |
| `./sync_to_zafin_private.sh "message"` | Sync with custom commit message |
| `rm -rf /tmp/zafin-private-sync` | Clear temp clone (for fresh start) |
| `ls AQ-ZAFIN-2026/` | View local Zafin files |
| `find AQ-ZAFIN-2026 -name "*.md"` | List all markdown files |

## Private Repo URL

https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture

---

## Key Documents

### Persona-Based Observability Framework

Addresses Rani Pendse's 3 open questions from the Feb 5, 2026 meeting:

1. **Q: Persona-Based Observability** - Who uses what tools (Developers vs SecOps vs SREs)
2. **Q: Infrastructure as Code** - Bicep, Terraform, azd patterns for AI Foundry
3. **Q: Bring Your Own Model/Tracing** - Customer endpoints + observability pipelines

Files:
- `PERSONA_BASED_OBSERVABILITY_FRAMEWORK.md` (source)
- `PERSONA_BASED_OBSERVABILITY_FRAMEWORK3.docx` (latest Word version)

### SRE Agent Reference

Full documentation for Azure SRE Agent implementation:
- `SRE-AGENT-REFERENCE.md` - Main reference
- `sre-agent-main/` - Official samples and Bicep deployments

---

## Setup Instructions (One-Time)

### 1. Create Private GitHub Repo

✅ Already created: https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture

### 2. Make Script Executable

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public
chmod +x sync_to_zafin_private.sh
```

### 3. Test Sync

```bash
./sync_to_zafin_private.sh "Initial sync"
```

### 4. Verify

Check the private repo: https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture

---

**Created:** February 5, 2026  
**Questions?** The script provides helpful error messages and confirmation prompts.
