#!/usr/bin/env bash

# Update maf-upstream/ by mirroring the latest microsoft/agent-framework working tree.
#
# Usage:
#   ./update_maf_upstream.sh
#   ./update_maf_upstream.sh --branch main
#   ./update_maf_upstream.sh --tag vX.Y.Z
#
# Notes:
# - This mirrors the upstream repo into maf-upstream/ using rsync --delete.
# - It does NOT touch this repo's git remotes/branches; it just updates the folder contents.

set -euo pipefail

UPSTREAM_REPO="https://github.com/microsoft/agent-framework.git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/maf-upstream"

REF_TYPE=""   # "branch" | "tag" | ""
REF_NAME=""   # name of branch/tag

print_usage() {
  cat <<'USAGE'
Update maf-upstream/ from microsoft/agent-framework.

Usage:
  ./update_maf_upstream.sh [--branch <name>] [--tag <name>]

Options:
  --branch <name>   Checkout a specific branch (default: repo default)
  --tag <name>      Checkout a specific tag
  -h, --help        Show this help

Examples:
  ./update_maf_upstream.sh
  ./update_maf_upstream.sh --branch main
  ./update_maf_upstream.sh --tag v1.2.3
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      REF_TYPE="branch"; REF_NAME="${2:-}"; shift 2 ;;
    --tag)
      REF_TYPE="tag"; REF_NAME="${2:-}"; shift 2 ;;
    -h|--help)
      print_usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      print_usage >&2
      exit 2
      ;;
  esac
done

if [[ -n "$REF_TYPE" && -z "$REF_NAME" ]]; then
  echo "Error: --$REF_TYPE requires a value" >&2
  exit 2
fi

if [[ ! -d "$SCRIPT_DIR" || ! -f "$SCRIPT_DIR/README.md" ]]; then
  echo "Error: run this from the agent-framework-public repo root." >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: target directory not found: $TARGET_DIR" >&2
  echo "Create it (or add it to the repo) before running this script." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is required." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/maf-upstream.XXXXXXXX")"
cleanup() {
  rm -rf "$TMP_DIR" >/dev/null 2>&1 || true
}
trap cleanup EXIT

CLONE_DIR="$TMP_DIR/agent-framework"

echo "=== Updating maf-upstream/ ==="
echo "Upstream: $UPSTREAM_REPO"

if [[ -n "$REF_TYPE" ]]; then
  echo "Ref: $REF_TYPE $REF_NAME"
fi

echo "Cloning upstream into temp dir..."
case "$REF_TYPE" in
  branch)
    git clone --depth 1 --branch "$REF_NAME" "$UPSTREAM_REPO" "$CLONE_DIR" ;;
  tag)
    git clone --depth 1 --branch "$REF_NAME" "$UPSTREAM_REPO" "$CLONE_DIR" ;;
  "")
    git clone --depth 1 "$UPSTREAM_REPO" "$CLONE_DIR" ;;
  *)
    echo "Internal error: unsupported ref type '$REF_TYPE'" >&2
    exit 1
    ;;
esac

# Mirror into maf-upstream/ (excluding .git just in case)
echo "Syncing into: $TARGET_DIR"
rsync -a --delete --exclude '.git' "$CLONE_DIR/" "$TARGET_DIR/"

echo "Done. Review changes with:"
echo "  git status"
echo "  git diff"
