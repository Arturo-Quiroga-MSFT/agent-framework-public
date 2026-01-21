#!/bin/bash

# Partner Directory OneDrive Sync Script
# Copies partner directories to OneDrive for Business for easy sharing

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PARTNER_DIRS=("AQ-ZAFIN-2026" "AQ-PROFISEE" "AQ-TERADATA" "AQ-THOUGHTWORKS-2026")
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Auto-detect OneDrive for Business paths
ONEDRIVE_PATHS=(
    "$HOME/onedrive-msft/OneDrive - Microsoft"
    "$HOME/OneDrive - Microsoft"
    "$HOME/Library/CloudStorage/OneDrive-Microsoft"
    "$HOME/OneDrive"
    "$HOME/Library/CloudStorage/OneDrive-*"
)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Partner → OneDrive Sync Tool${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to find OneDrive path
find_onedrive() {
    for path_pattern in "${ONEDRIVE_PATHS[@]}"; do
        # Handle wildcards
        for path in $path_pattern; do
            if [ -d "$path" ]; then
                echo "$path"
                return 0
            fi
        done
    done
    return 1
}

# Find or prompt for OneDrive path
ONEDRIVE_BASE=""
if DETECTED_PATH=$(find_onedrive); then
    echo -e "${GREEN}✓ Found OneDrive: $DETECTED_PATH${NC}"
    ONEDRIVE_BASE="$DETECTED_PATH"
else
    echo -e "${YELLOW}⚠ Could not auto-detect OneDrive path.${NC}"
    echo ""
    read -p "Enter your OneDrive path (or Q to quit): " user_path
    
    if [[ "$user_path" =~ ^[Qq]$ ]]; then
        echo "Sync cancelled."
        exit 0
    fi
    
    # Expand tilde
    user_path="${user_path/#\~/$HOME}"
    
    if [ ! -d "$user_path" ]; then
        echo -e "${RED}✗ Path not found: $user_path${NC}"
        exit 1
    fi
    
    ONEDRIVE_BASE="$user_path"
fi

# Create partner sync folder in OneDrive
SYNC_FOLDER="$ONEDRIVE_BASE/Partner-Engagements"
mkdir -p "$SYNC_FOLDER"

echo -e "${BLUE}Sync destination: $SYNC_FOLDER${NC}"
echo ""

# Function to sync a single partner directory
sync_partner() {
    local partner_dir=$1
    
    if [ ! -d "$partner_dir" ]; then
        echo -e "${YELLOW}⊘ Skipping $partner_dir (not found)${NC}"
        return 1
    fi
    
    local dest_dir="$SYNC_FOLDER/$partner_dir"
    
    echo -e "${BLUE}📁 Syncing $partner_dir...${NC}"
    
    # Create destination if it doesn't exist
    mkdir -p "$dest_dir"
    
    # Use rsync for efficient copying (only copies changed files)
    rsync -av --delete \
        --exclude='.DS_Store' \
        --exclude='__pycache__' \
        --exclude='.pytest_cache' \
        --exclude='.venv' \
        --exclude='.vscode' \
        --exclude='node_modules' \
        --exclude='.git' \
        "$partner_dir/" "$dest_dir/" \
        2>&1 | grep -v "building file list\|sending incremental\|sent\|total size" || true
    
    local size=$(du -sh "$dest_dir" | cut -f1)
    echo -e "${GREEN}✓ Synced to: $dest_dir (${size})${NC}"
    echo ""
    
    return 0
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments - interactive mode
    echo -e "${YELLOW}Available partner directories:${NC}"
    for i in "${!PARTNER_DIRS[@]}"; do
        echo "  $((i+1)). ${PARTNER_DIRS[$i]}"
    done
    echo "  A. All partners"
    echo ""
    read -p "Select partner(s) to sync (1-${#PARTNER_DIRS[@]}, A for all, or Q to quit): " choice
    
    if [[ "$choice" =~ ^[Qq]$ ]]; then
        echo "Sync cancelled."
        exit 0
    elif [[ "$choice" =~ ^[Aa]$ ]]; then
        # Sync all
        echo ""
        for partner in "${PARTNER_DIRS[@]}"; do
            sync_partner "$partner"
        done
    elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#PARTNER_DIRS[@]}" ]; then
        # Sync specific partner
        echo ""
        sync_partner "${PARTNER_DIRS[$((choice-1))]}"
    else
        echo -e "${RED}Invalid selection.${NC}"
        exit 1
    fi
else
    # Command line arguments provided
    case "$1" in
        --all|-a)
            echo -e "${BLUE}Syncing all partner directories...${NC}"
            echo ""
            for partner in "${PARTNER_DIRS[@]}"; do
                sync_partner "$partner"
            done
            ;;
        --zafin)
            sync_partner "AQ-ZAFIN-2026"
            ;;
        --profisee)
            sync_partner "AQ-PROFISEE"
            ;;
        --teradata)
            sync_partner "AQ-TERADATA"
            ;;
        --thoughtworks)
            sync_partner "AQ-THOUGHTWORKS-2026"
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Sync partner directories to OneDrive for Business."
            echo ""
            echo "Options:"
            echo "  (no args)         Interactive mode"
            echo "  -a, --all         Sync all partner directories"
            echo "  --zafin           Sync AQ-ZAFIN-2026 only"
            echo "  --profisee        Sync AQ-PROFISEE only"
            echo "  --teradata        Sync AQ-TERADATA only"
            echo "  --thoughtworks    Sync AQ-THOUGHTWORKS-2026 only"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Interactive mode"
            echo "  $0 --all              # Sync all partners"
            echo "  $0 --zafin            # Sync Zafin only"
            echo ""
            echo "Notes:"
            echo "  - Uses rsync for efficient incremental sync"
            echo "  - Only copies changed files"
            echo "  - Removes deleted files from OneDrive (--delete)"
            echo "  - Auto-detects OneDrive path"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Sync complete!${NC}"
echo ""
echo -e "${YELLOW}OneDrive location:${NC}"
echo -e "  ${SYNC_FOLDER}/"
echo ""
echo -e "${YELLOW}To share with partners:${NC}"
echo "  1. Right-click folder in OneDrive"
echo "  2. Select 'Share' → 'Share with specific people'"
echo "  3. Enter partner email addresses"
echo "  4. Set permissions (View/Edit)"
echo ""
echo -e "${YELLOW}To automate syncing:${NC}"
echo "  # Add to crontab for daily sync at 6 PM:"
echo "  0 18 * * * cd $(pwd) && ./sync_to_onedrive.sh --all"
echo ""
