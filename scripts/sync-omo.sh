#!/usr/bin/env bash
# sync-omo.sh - keep the repo's omo.jsonc and the live plugin config in sync.
#
# The oh-my-openagent plugin (>=4.19) reads its config from ~/.omo/omo.jsonc.
# This repo version-controls the canonical copy at <repo>/omo.jsonc.
# We deliberately do NOT symlink: the plugin's config migration can rewrite
# the target path, and a symlink makes that hard to notice.
#
# Usage:
#   scripts/sync-omo.sh push    # repo  -> ~/.omo/omo.jsonc  (after editing the repo copy)
#   scripts/sync-omo.sh pull    # ~/.omo/omo.jsonc -> repo   (after the plugin migrates/writes it)
#   scripts/sync-omo.sh check   # diff the two, exit 1 if they differ
#   scripts/sync-omo.sh doctor  # validate JSONC + run plugin doctor + list agents

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_CONFIG="$REPO_DIR/omo.jsonc"
LIVE_DIR="$HOME/.omo"
LIVE_CONFIG="$LIVE_DIR/omo.jsonc"

validate_jsonc() {
  grep -v "^\s*//" "$1" | python3 -c "import json,sys,re; json.loads(re.sub(r',(\s*[}\]])', r'\1', sys.stdin.read()))" > /dev/null
}

cmd="${1:-check}"

case "$cmd" in
  push)
    validate_jsonc "$REPO_CONFIG" || { echo "ERROR: $REPO_CONFIG is not valid JSONC"; exit 1; }
    mkdir -p "$LIVE_DIR"
    if [ -f "$LIVE_CONFIG" ] && ! diff -q "$REPO_CONFIG" "$LIVE_CONFIG" > /dev/null 2>&1; then
      cp "$LIVE_CONFIG" "$LIVE_CONFIG.bak.$(date -u +%Y-%m-%dT%H-%M-%SZ)"
      echo "Backed up existing live config."
    fi
    cp "$REPO_CONFIG" "$LIVE_CONFIG"
    echo "Pushed $REPO_CONFIG -> $LIVE_CONFIG"
    ;;
  pull)
    [ -f "$LIVE_CONFIG" ] || { echo "ERROR: $LIVE_CONFIG does not exist"; exit 1; }
    validate_jsonc "$LIVE_CONFIG" || { echo "ERROR: $LIVE_CONFIG is not valid JSONC"; exit 1; }
    cp "$LIVE_CONFIG" "$REPO_CONFIG"
    echo "Pulled $LIVE_CONFIG -> $REPO_CONFIG (review with: git diff omo.jsonc)"
    ;;
  check)
    if [ ! -f "$LIVE_CONFIG" ]; then
      echo "MISSING: $LIVE_CONFIG (run: scripts/sync-omo.sh push)"
      exit 1
    fi
    if diff -q "$REPO_CONFIG" "$LIVE_CONFIG" > /dev/null 2>&1; then
      echo "IN SYNC: repo and live config are identical."
    else
      echo "OUT OF SYNC:"
      diff "$REPO_CONFIG" "$LIVE_CONFIG" | head -40 || true
      echo ""
      echo "Resolve with: scripts/sync-omo.sh push  (repo wins)"
      echo "         or:  scripts/sync-omo.sh pull  (live wins)"
      exit 1
    fi
    ;;
  doctor)
    validate_jsonc "$REPO_CONFIG" && echo "JSONC: valid"
    BIN="$(ls -d "$HOME"/.cache/opencode/packages/oh-my-openagent@*/node_modules/.bin/oh-my-openagent 2>/dev/null | sort -V | tail -1)"
    [ -n "$BIN" ] && [ -x "$BIN" ] && "$BIN" doctor || echo "(plugin CLI not found, skipping doctor)"
    opencode agent list 2>/dev/null | grep -oP "^[\w -]+ \((primary|subagent|all)\)" || true
    ;;
  *)
    echo "Usage: $0 {push|pull|check|doctor}" >&2
    exit 2
    ;;
esac
