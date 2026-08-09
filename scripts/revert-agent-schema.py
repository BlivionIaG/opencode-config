#!/usr/bin/env python3
"""Revert (normalize) omo.jsonc from modern `models:[]` format back to
canonical `model + fallback_models`.

This is a thin wrapper around `scripts/lint-omo-config.py --fix`. The
linter is the source of truth; this script exists for backward
compatibility with older docs/instructions that name it.

WHY (kept for context)
======================
The plugin's runtime schema (oh-my-opencode plugin) only extracts
`model`, `fallback_models`, `variant`, `thinking`, etc. from agents
and categories at runtime. The `models:[]` array is **dropped** — the
runtime falls back to the plugin's built-in defaults.

Format rules:
  - Agents under `[opencode].agents.*` use `model + fallback_models`
  - Categories under `[opencode].categories.*` use `model + fallback_models`

USAGE
=====
    scripts/revert-agent-schema.py                  # auto-fix omo.jsonc
    scripts/revert-agent-schema.py --check omo.jsonc  # report only
    scripts/revert-agent-schema.py path/to/file omo.jsonc  # explicit path
"""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LINT_SCRIPT = SCRIPT_DIR / "lint-omo-config.py"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Revert omo.jsonc to canonical model + fallback_models "
                    "format (delegates to lint-omo-config.py).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="omo.jsonc",
        help="Path to omo.jsonc (default: omo.jsonc)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only report what would change; do not write",
    )
    args = parser.parse_args()

    if not LINT_SCRIPT.exists():
        print(f"ERROR: {LINT_SCRIPT} not found", file=sys.stderr)
        return 2

    cmd = [sys.executable, str(LINT_SCRIPT), args.path]
    if args.check:
        cmd.append("--check")
    else:
        cmd.append("--fix")

    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
