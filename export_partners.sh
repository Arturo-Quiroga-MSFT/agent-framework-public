#!/bin/bash

# Partner Directory Export Script
# Creates zip archives of partner directories for sharing

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PARTNER_DIRS=("AQ-ZAFIN-2026" "AQ-PROFISEE" "AQ-TERADATA" "AQ-THOUGHTWORKS-2026")
EXPORT_DIR="./partner-exports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Partner Directory Export Tool${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create export directory if it doesn't exist
mkdir -p "$EXPORT_DIR"

# Function to zip a single partner directory
zip_partner() {
    local partner_dir=$1
    
    if [ ! -d "$partner_dir" ]; then
        echo -e "${YELLOW}⊘ Skipping $partner_dir (not found)${NC}"
        return 1
    fi
    
    local partner_name=$(echo "$partner_dir" | tr '[:upper:]' '[:lower:]')
    local zip_file="$EXPORT_DIR/${partner_name}-${TIMESTAMP}.zip"
    
    echo -e "${BLUE}📦 Zipping $partner_dir...${NC}"
    
    # Create zip excluding .git and other unnecessary files
    zip -r "$zip_file" "$partner_dir" \
        -x "*.DS_Store" \
        -x "*/__pycache__/*" \
        -x "*/.pytest_cache/*" \
        -x "*/.venv/*" \
        -x "*/.vscode/*" \
        -x "*/node_modules/*" \
        -x "*/.git/*" \
        > /dev/null 2>&1
    
    local size=$(du -h "$zip_file" | cut -f1)
    echo -e "${GREEN}✓ Created: $zip_file (${size})${NC}"
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
    read -p "Select partner(s) to export (1-${#PARTNER_DIRS[@]}, A for all, or Q to quit): " choice
    
    if [[ "$choice" =~ ^[Qq]$ ]]; then
        echo "Export cancelled."
        exit 0
    elif [[ "$choice" =~ ^[Aa]$ ]]; then
        # Export all
        echo ""
        for partner in "${PARTNER_DIRS[@]}"; do
            zip_partner "$partner"
        done
    elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#PARTNER_DIRS[@]}" ]; then
        # Export specific partner
        echo ""
        zip_partner "${PARTNER_DIRS[$((choice-1))]}"
    else
        echo -e "${RED}Invalid selection.${NC}"
        exit 1
    fi
else
    # Command line arguments provided
    case "$1" in
        --all|-a)
            echo -e "${BLUE}Exporting all partner directories...${NC}"
            echo ""
            for partner in "${PARTNER_DIRS[@]}"; do
                zip_partner "$partner"
            done
            ;;
        --zafin)
            zip_partner "AQ-ZAFIN-2026"
            ;;
        --profisee)
            zip_partner "AQ-PROFISEE"
            ;;
        --teradata)
            zip_partner "AQ-TERADATA"
            ;;
        --thoughtworks)
            zip_partner "AQ-THOUGHTWORKS-2026"
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Export partner directories as zip archives for sharing."
            echo ""
            echo "Options:"
            echo "  (no args)         Interactive mode"
            echo "  -a, --all         Export all partner directories"
            echo "  --zafin           Export AQ-ZAFIN-2026 only"
            echo "  --profisee        Export AQ-PROFISEE only"
            echo "  --teradata        Export AQ-TERADATA only"
            echo "  --thoughtworks    Export AQ-THOUGHTWORKS-2026 only"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Interactive mode"
            echo "  $0 --all              # Export all partners"
            echo "  $0 --zafin            # Export Zafin only"
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
echo -e "${GREEN}✓ Export complete!${NC}"
echo ""
echo -e "${YELLOW}Exported files location:${NC}"
echo -e "  ${EXPORT_DIR}/"
echo ""
echo -e "${YELLOW}To share:${NC}"
echo "  1. Email the zip file(s) to partner contacts"
echo "  2. Upload to OneDrive/SharePoint"
echo "  3. Share via Teams"
echo ""
echo -e "${YELLOW}To clean up old exports:${NC}"
echo "  rm ${EXPORT_DIR}/*.zip"
echo ""
