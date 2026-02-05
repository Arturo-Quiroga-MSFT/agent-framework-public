#!/bin/bash

# sync_to_zafin_private.sh
# Syncs AQ-ZAFIN-2026 directory to private zafin-multi-agent-architecture repo
# Uses rsync method - works with gitignored directories (keeps public repo clean)
# Usage: ./sync_to_zafin_private.sh [commit-message]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PUBLIC_REPO_DIR="/Users/arturoquiroga/GITHUB/agent-framework-public"
ZAFIN_DIR="AQ-ZAFIN-2026"
PRIVATE_REPO_URL="https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture.git"
PRIVATE_CLONE_DIR="/tmp/zafin-private-sync"
PRIVATE_BRANCH="main"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Zafin Materials Sync Tool (rsync method)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "$ZAFIN_DIR" ]; then
    echo -e "${RED}❌ Error: Must run from repository root${NC}"
    echo -e "${YELLOW}   Current directory: $(pwd)${NC}"
    echo -e "${YELLOW}   Expected: $PUBLIC_REPO_DIR${NC}"
    exit 1
fi

# Get commit message
if [ -z "$1" ]; then
    echo -e "${BLUE}Enter commit message:${NC}"
    read -r COMMIT_MSG
else
    COMMIT_MSG="$1"
fi

# Show what will be synced
echo ""
echo -e "${BLUE}📊 Files to sync from ${ZAFIN_DIR}/:${NC}"
find "$ZAFIN_DIR" -type f -name "*.md" | head -10 | sed 's/^/   /'
FILE_COUNT=$(find "$ZAFIN_DIR" -type f | wc -l | tr -d ' ')
echo -e "   ${YELLOW}... and ${FILE_COUNT} total files${NC}"
echo ""

# Confirm sync
read -p "$(echo -e ${BLUE}Sync these files to private repo? \(y/n\) ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Sync cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Starting sync...${NC}"
echo ""

# Step 1: Clone or update private repo
echo -e "${BLUE}📥 Preparing private repo clone...${NC}"
if [ -d "$PRIVATE_CLONE_DIR/.git" ]; then
    echo -e "   Updating existing clone..."
    pushd "$PRIVATE_CLONE_DIR" > /dev/null
    git fetch origin
    git reset --hard origin/$PRIVATE_BRANCH
    popd > /dev/null
else
    echo -e "   Cloning private repo..."
    rm -rf "$PRIVATE_CLONE_DIR"
    git clone "$PRIVATE_REPO_URL" "$PRIVATE_CLONE_DIR"
fi
echo -e "${GREEN}   ✓ Private repo ready${NC}"
echo ""

# Step 2: Rsync files (excluding _local and other private dirs)
echo -e "${BLUE}📦 Syncing files...${NC}"
rsync -av --delete \
    --exclude='.git/' \
    --exclude='_local/' \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    --exclude='__pycache__/' \
    "$ZAFIN_DIR/" "$PRIVATE_CLONE_DIR/"

echo -e "${GREEN}   ✓ Files synced${NC}"
echo ""

# Step 3: Commit and push
echo -e "${BLUE}📤 Committing and pushing...${NC}"
pushd "$PRIVATE_CLONE_DIR" > /dev/null

# Check if there are changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}   No changes to commit - already up to date${NC}"
    popd > /dev/null
else
    git add -A
    git commit -m "$COMMIT_MSG"
    git push origin $PRIVATE_BRANCH
    echo -e "${GREEN}   ✓ Changes pushed${NC}"
    popd > /dev/null
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Sync complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Private repo URL:${NC}"
echo -e "   https://github.com/Arturo-Quiroga-MSFT/zafin-multi-agent-architecture"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "   ${GREEN}✓${NC} AQ-ZAFIN-2026/ synced to private repo"
echo -e "   ${GREEN}✓${NC} Public repo stays clean (files gitignored)"
echo -e "   ${GREEN}✓${NC} Team members can pull latest changes"
echo ""
