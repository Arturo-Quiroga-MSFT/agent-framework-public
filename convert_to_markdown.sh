#!/usr/bin/env bash

# =============================================================================
# convert_to_markdown.sh
# =============================================================================
#
# PURPOSE
#   Converts .docx and .pptx files to Markdown (.md) for use as grounding
#   documents, knowledge bases, or readable reference material.
#
# TOOLS USED
#   - pandoc     → .docx conversion (preserves headings, tables, links, bold/italic)
#   - markitdown → .pptx conversion (preserves slide titles, bullets, speaker notes)
#     (markitdown also handles .docx; pandoc is preferred for docx as it gives
#     richer table output via GitHub Flavored Markdown format)
#
# INSTALL DEPENDENCIES (one-time)
#   brew install pandoc
#   pip install markitdown[pptx]          # or: pip install markitdown[all]
#
# USAGE
#   ./convert_to_markdown.sh [PATH] [OPTIONS]
#
# ARGUMENTS
#   PATH          File or directory to convert.
#                 - If a file:      converts that file only
#                 - If a directory: converts all .docx and .pptx files found
#                                   (non-recursive by default; use --recursive)
#                 - If omitted:     uses current directory
#
# OPTIONS
#   --recursive   Also search subdirectories
#   --force       Overwrite existing .md files (default: skip already-converted)
#   --output DIR  Write .md files to DIR instead of alongside source files
#   --dry-run     Show what would be converted without doing it
#   -h, --help    Show this help and exit
#
# OUTPUT
#   Each converted file gets a .md file with the same base name.
#   Example:  my_deck.pptx  →  my_deck.md
#             proposal.docx →  proposal.md
#
# WHAT IS PRESERVED
#   .docx (via pandoc --to gfm):
#     ✅ Headings (H1–H6)        ✅ Tables         ✅ Bold / italic
#     ✅ Bullet / numbered lists  ✅ Hyperlinks     ✅ Blockquotes
#     ⚠️  Images → dropped (referenced as paths if embedded)
#     ⚠️  Comments/tracked changes → stripped
#
#   .pptx (via markitdown):
#     ✅ Slide titles as headings  ✅ Bullet content  ✅ Speaker notes
#     ✅ Tables inside slides      ✅ Text in shapes
#     ⚠️  Images / charts → dropped (text alt only if present)
#     ⚠️  Multi-column layouts → linearized
#
# EXAMPLES
#   # Convert all docs in current directory
#   ./convert_to_markdown.sh
#
#   # Convert a specific file
#   ./convert_to_markdown.sh "AQ-CERENCE-2026/grounding_docs/my_deck.pptx"
#
#   # Convert entire partner folder recursively, output to a separate folder
#   ./convert_to_markdown.sh AQ-CERENCE-2026 --recursive --output AQ-CERENCE-2026/converted_md
#
#   # Preview what would be converted without touching files
#   ./convert_to_markdown.sh AQ-ZAFIN-2026 --recursive --dry-run
#
#   # Force reconvert even if .md already exists
#   ./convert_to_markdown.sh AQ-PROFISEE --recursive --force
#
# =============================================================================

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'

# ── Defaults ──────────────────────────────────────────────────────────────────
SEARCH_PATH="."
RECURSIVE=false
FORCE=false
OUTPUT_DIR=""
DRY_RUN=false

# ── Counters ──────────────────────────────────────────────────────────────────
COUNT_CONVERTED=0
COUNT_SKIPPED=0
COUNT_FAILED=0

# ── Detect tool paths ─────────────────────────────────────────────────────────
# Prefer venv markitdown if running from repo root
VENV_MARKITDOWN="$(pwd)/.venv/bin/markitdown"
if [ -x "$VENV_MARKITDOWN" ]; then
    MARKITDOWN="$VENV_MARKITDOWN"
elif command -v markitdown &>/dev/null; then
    MARKITDOWN="$(command -v markitdown)"
else
    MARKITDOWN=""
fi

if command -v pandoc &>/dev/null; then
    PANDOC="$(command -v pandoc)"
else
    PANDOC=""
fi

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            grep -A 80 '^# PURPOSE' "$0" | grep '^#' | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        --recursive)
            RECURSIVE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            exit 1
            ;;
        *)
            SEARCH_PATH="$1"
            shift
            ;;
    esac
done

# ── Validate dependencies ─────────────────────────────────────────────────────
check_deps() {
    local missing=()
    [ -z "$PANDOC" ] && missing+=("pandoc  →  brew install pandoc")
    [ -z "$MARKITDOWN" ] && missing+=("markitdown  →  pip install markitdown[pptx]")
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing dependencies:${NC}"
        for m in "${missing[@]}"; do
            echo -e "   ${YELLOW}$m${NC}"
        done
        echo ""
        echo -e "${GRAY}Install both and re-run. Only the relevant tool is required for each format.${NC}"
        exit 1
    fi
}

# ── Convert a single file ─────────────────────────────────────────────────────
convert_file() {
    local src="$1"
    local ext="${src##*.}"
    ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"   # lowercase, macOS-safe

    # Determine output path
    local base
    base="$(basename "${src%.*}")"
    local src_dir
    src_dir="$(dirname "$src")"

    if [ -n "$OUTPUT_DIR" ]; then
        mkdir -p "$OUTPUT_DIR"
        local dest="${OUTPUT_DIR}/${base}.md"
    else
        local dest="${src_dir}/${base}.md"
    fi

    # Skip check
    if [ -f "$dest" ] && [ "$FORCE" = false ]; then
        echo -e "  ${GRAY}SKIP${NC}  $(basename "$dest")  ${GRAY}(already exists — use --force to overwrite)${NC}"
        COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
        return
    fi

    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}DRY ${NC}  $src  ${GRAY}→  $dest${NC}"
        COUNT_CONVERTED=$((COUNT_CONVERTED + 1))
        return
    fi

    # Run conversion
    local ok=false
    case "$ext" in
        docx)
            if [ -z "$PANDOC" ]; then
                echo -e "  ${RED}FAIL${NC}  $(basename "$src")  ${RED}(pandoc not found)${NC}"
                COUNT_FAILED=$((COUNT_FAILED + 1))
                return
            fi
            if "$PANDOC" "$src" -t gfm -o "$dest" 2>/dev/null; then
                ok=true
            fi
            ;;
        pptx)
            if [ -z "$MARKITDOWN" ]; then
                echo -e "  ${RED}FAIL${NC}  $(basename "$src")  ${RED}(markitdown not found)${NC}"
                COUNT_FAILED=$((COUNT_FAILED + 1))
                return
            fi
            if "$MARKITDOWN" "$src" > "$dest" 2>/dev/null; then
                ok=true
            fi
            ;;
    esac

    if [ "$ok" = true ]; then
        local size
        size=$(wc -l < "$dest")
        echo -e "  ${GREEN}DONE${NC}  $(basename "$src")  ${GRAY}→  $(basename "$dest")  (${size} lines)${NC}"
        COUNT_CONVERTED=$((COUNT_CONVERTED + 1))
    else
        rm -f "$dest"    # clean up empty file on failure
        echo -e "  ${RED}FAIL${NC}  $(basename "$src")"
        COUNT_FAILED=$((COUNT_FAILED + 1))
    fi
}

# ── Find and collect files ─────────────────────────────────────────────────────
collect_files() {
    if [ -f "$SEARCH_PATH" ]; then
        echo "$SEARCH_PATH"
        return
    fi

    if [ ! -d "$SEARCH_PATH" ]; then
        echo -e "${RED}❌ Path not found: $SEARCH_PATH${NC}" >&2
        exit 1
    fi

    local depth_flag="-maxdepth 1"
    [ "$RECURSIVE" = true ] && depth_flag=""

    # Use find; sort for consistent ordering
    eval find \""$SEARCH_PATH"\" $depth_flag -type f \\\( -iname '"*.docx"' -o -iname '"*.pptx"' \\\) | sort
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}   convert_to_markdown.sh${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    [ "$DRY_RUN" = true ] && echo -e "${YELLOW}⚠️  DRY RUN — no files will be written${NC}\n"

    check_deps

    # Show tool versions
    echo -e "${GRAY}pandoc:     $("$PANDOC" --version | head -1)${NC}"
    echo -e "${GRAY}markitdown: $("$MARKITDOWN" --version 2>/dev/null || echo 'installed')${NC}"
    echo -e "${GRAY}source:     $SEARCH_PATH$( [ "$RECURSIVE" = true ] && echo ' (recursive)')${NC}"
    [ -n "$OUTPUT_DIR" ] && echo -e "${GRAY}output dir: $OUTPUT_DIR${NC}"
    echo ""

    # Collect and process
    local files=()
    while IFS= read -r line; do
        files+=("$line")
    done < <(collect_files)

    if [ ${#files[@]} -eq 0 ]; then
        echo -e "${YELLOW}No .docx or .pptx files found in: $SEARCH_PATH${NC}"
        exit 0
    fi

    echo -e "${BLUE}Found ${#files[@]} file(s):${NC}"
    for f in "${files[@]}"; do
        convert_file "$f"
    done

    # Summary
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    [ "$DRY_RUN" = true ] && echo -e "  ${CYAN}Would convert:${NC}  $COUNT_CONVERTED"
    [ "$DRY_RUN" = false ] && echo -e "  ${GREEN}Converted:${NC}  $COUNT_CONVERTED"
    echo -e "  ${GRAY}Skipped:${NC}    $COUNT_SKIPPED"
    [ $COUNT_FAILED -gt 0 ] && echo -e "  ${RED}Failed:${NC}     $COUNT_FAILED"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

main
