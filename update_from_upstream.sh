#!/bin/bash

# Script to update specific directories from Microsoft's agent-framework repository
# Usage: ./update_from_upstream.sh

set -e  # Exit on error

UPSTREAM_REPO="https://github.com/microsoft/agent-framework.git"
TEMP_DIR="temp_upstream_clone"
DIRECTORIES=("docs" "dotnet" "python" "workflow-samples")

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Agent Framework Update Script ===${NC}"
echo -e "${BLUE}Updating from: ${UPSTREAM_REPO}${NC}\n"

# Get the script's directory (where the script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we're in the right directory
if [ ! -f "$SCRIPT_DIR/README.md" ]; then
    echo -e "${RED}Error: This script must be run from the agent-framework-public repository root${NC}"
    exit 1
fi

# Remove temp directory if it exists from a previous run
if [ -d "$TEMP_DIR" ]; then
    echo -e "${YELLOW}Removing old temporary directory...${NC}"
    rm -rf "$TEMP_DIR"
fi

# Clone the upstream repository
echo -e "${BLUE}Cloning upstream repository...${NC}"
git clone --depth 1 "$UPSTREAM_REPO" "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to clone upstream repository${NC}"
    exit 1
fi

echo -e "${GREEN}Clone successful!${NC}\n"

# Update each directory
for dir in "${DIRECTORIES[@]}"; do
    echo -e "${BLUE}Processing directory: ${dir}${NC}"
    
    # Check if directory exists in upstream
    if [ ! -d "$TEMP_DIR/$dir" ]; then
        echo -e "${YELLOW}Warning: Directory '$dir' not found in upstream repository, skipping...${NC}\n"
        continue
    fi
    
    # Backup existing directory if it exists
    if [ -d "$SCRIPT_DIR/$dir" ]; then
        echo -e "${YELLOW}  - Removing existing directory: $dir${NC}"
        rm -rf "$SCRIPT_DIR/$dir"
    fi
    
    # Copy from upstream
    echo -e "${GREEN}  - Copying from upstream...${NC}"
    cp -R "$TEMP_DIR/$dir" "$SCRIPT_DIR/$dir"
    
    echo -e "${GREEN}  ✓ Successfully updated: $dir${NC}\n"
done

# Clean up temporary directory
echo -e "${BLUE}Cleaning up temporary files...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}=== Update Complete ===${NC}"
echo -e "${YELLOW}Note: Changes have been applied locally. Review changes with:${NC}"
echo -e "  git status"
echo -e "  git diff"
echo -e "${YELLOW}If satisfied, commit and push the changes.${NC}"
