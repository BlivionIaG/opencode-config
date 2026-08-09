#!/usr/bin/env python3
"""Lint and optionally normalize omo.jsonc to canonical format.

WHY
===
The plugin's runtime schema in oh-my-openagent (oh-my-opencode plugin) only
extracts `model`, `fallback_models`, `variant`, `thinking`, etc. from
agents and categories at runtime (see `modelInput` in cli-node/index.js,
around line 104215). The `models:[]` array is **dropped** — the runtime
falls back to the plugin's built-in defaults (e.g. `claude-fable-5`,
`gpt-5.6-sol`, `kimi-for-coding-highspeed`).

This is true for BOTH agents AND categories, even though the
`scripts/revert-agent-schema.py` docstring previously claimed categories
"correctly use models:[]". That claim was wrong — categories need the
same legacy `model + fallback_models` form as agents for the plugin
runtime to pick them up.

Format rules this linter enforces:
  - Agents under `[opencode].agents.*` use `model + fallback_models`
  - Categories under `[opencode].categories.*` use `model + fallback_models`
  - `model` is a non-empty string
  - `fallback_models` is an array of non-empty strings
  - `reasoning` (if present) is one of the plugin's enum values
  - `thinking.type` (if present) is "enabled" or "disabled"

USAGE
=====
    scripts/lint-omo-config.py                  # check current omo.jsonc
    scripts/lint-omo-config.py --check         # same as default (no writes)
    scripts/lint-omo-config.py --fix           # auto-convert to canonical
    scripts/lint-omo-config.py path/to/file    # lint a specific file

Exit codes:
  0 = no issues (or issues fixed with --fix)
  1 = issues found (not auto-fixed)
  2 = parse error / file not found
"""
import argparse
import json
import re
import sys
from pathlib import Path


VALID_REASONING = {
    "off", "minimal", "low", "medium", "high", "xhigh", "max", "auto",
    "none",  # legacy alias for "off"
}


def strip_jsonc_comments(text: str) -> str:
    return re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)


def load_jsonc(path: Path) -> dict:
    raw = path.read_text()
    raw = strip_jsonc_comments(raw)
    raw = re.sub(r",(\s*[}\]])", r"\1", raw)
    return json.loads(raw)


def write_jsonc(path: Path, data: dict, header: str = "// OMO configuration\n") -> None:
    raw = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(header + raw + "\n")


def is_valid_model_ref(value) -> bool:
    return isinstance(value, str) and len(value) > 0


def collect_entry_issues(
    name: str,
    entry: dict,
    *,
    slot: str,
) -> list[str]:
    """Return a list of human-readable issues for a single agent or category."""
    issues: list[str] = []

    has_model = "model" in entry
    has_fallback = "fallback_models" in entry
    has_models_array = "models" in entry

    if has_models_array and (has_model or has_fallback):
        issues.append(
            f"{slot}.{name}: has both 'models' (dropped at runtime) and "
            f"'model'/'fallback_models' — pick one"
        )
    elif has_models_array:
        issues.append(
            f"{slot}.{name}: 'models:[]' is dropped at runtime by the plugin's "
            f"modelInput extractor; use 'model' + 'fallback_models' instead"
        )
    elif not has_model:
        issues.append(
            f"{slot}.{name}: missing 'model' field (empty agent/category)"
        )
    elif not has_fallback:
        issues.append(
            f"{slot}.{name}: missing 'fallback_models' field "
            f"(plugin may fall back to defaults)"
        )

    if has_model:
        if not is_valid_model_ref(entry["model"]):
            issues.append(
                f"{slot}.{name}: 'model' must be a non-empty string, got "
                f"{entry['model']!r}"
            )

    if has_fallback:
        fb = entry["fallback_models"]
        if not isinstance(fb, list):
            issues.append(
                f"{slot}.{name}: 'fallback_models' must be an array, got "
                f"{type(fb).__name__}"
            )
        else:
            for i, ref in enumerate(fb):
                if not is_valid_model_ref(ref):
                    issues.append(
                        f"{slot}.{name}.fallback_models[{i}]: must be a "
                        f"non-empty string, got {ref!r}"
                    )

    if "reasoning" in entry:
        if entry["reasoning"] not in VALID_REASONING:
            issues.append(
                f"{slot}.{name}: 'reasoning'={entry['reasoning']!r} is not a "
                f"valid value (expected one of {sorted(VALID_REASONING)})"
            )

    thinking = entry.get("thinking")
    if isinstance(thinking, dict):
        ttype = thinking.get("type")
        if ttype not in ("enabled", "disabled"):
            issues.append(
                f"{slot}.{name}: 'thinking.type' must be 'enabled' or "
                f"'disabled', got {ttype!r}"
            )

    return issues


def collect_issues(config: dict) -> list[str]:
    opencode = config.get("[opencode]", {})
    issues: list[str] = []

    agents = opencode.get("agents", {})
    if isinstance(agents, dict):
        for name, entry in agents.items():
            if not isinstance(entry, dict):
                issues.append(f"agents.{name}: expected object, got {type(entry).__name__}")
                continue
            issues.extend(collect_entry_issues(name, entry, slot="agents"))

    categories = opencode.get("categories", {})
    if isinstance(categories, dict):
        for name, entry in categories.items():
            if not isinstance(entry, dict):
                issues.append(f"categories.{name}: expected object, got {type(entry).__name__}")
                continue
            issues.extend(collect_entry_issues(name, entry, slot="categories"))

    return issues


def normalize_entry(entry: dict) -> tuple[dict, bool]:
    """Convert a `models:[]` entry into `model + fallback_models`. Returns
    (new_entry, changed). Idempotent: returns (entry, False) if already
    canonical."""
    if "model" in entry or "models" not in entry:
        return dict(entry), False

    models = entry["models"]
    if not models:
        return dict(entry), False

    primary = models[0]
    fallbacks = list(models[1:])

    new_entry = {k: v for k, v in entry.items() if k != "models"}

    if isinstance(primary, dict):
        model_name = primary.get("model")
        if model_name is None:
            raise ValueError(f"primary slot missing 'model': {primary!r}")
        new_entry["model"] = model_name
        # Hoist per-model reasoning/thinking/variant/reasoningEffort up
        for key in ("reasoning", "variant", "reasoningEffort", "thinking"):
            if key in primary:
                new_entry[key] = primary[key]
    elif isinstance(primary, str):
        new_entry["model"] = primary
    else:
        raise ValueError(f"unexpected primary slot type: {type(primary).__name__}")

    new_entry["fallback_models"] = fallbacks
    return new_entry, True


def normalize_config(config: dict) -> tuple[dict, list[str]]:
    opencode = config.get("[opencode]", {})
    changes: list[str] = []

    for section in ("agents", "categories"):
        holders = opencode.get(section, {})
        if not isinstance(holders, dict):
            continue
        converted: dict[str, dict] = {}
        for name, entry in holders.items():
            if not isinstance(entry, dict):
                converted[name] = entry
                continue
            new_entry, changed = normalize_entry(entry)
            converted[name] = new_entry
            if changed:
                changes.append(f"{section}.{name}")
        opencode[section] = converted

    return config, changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("path", nargs="?", default="omo.jsonc")
    parser.add_argument("--check", action="store_true",
                        help="Only report issues; do not write (default)")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-convert modern 'models:[]' format to "
                             "canonical 'model + fallback_models'")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 2

    try:
        config = load_jsonc(path)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: {path} is not valid JSONC: {e}", file=sys.stderr)
        return 2

    issues = collect_issues(config)

    if args.fix:
        new_config, changes = normalize_config(config)
        new_issues = collect_issues(new_config)

        if changes:
            write_jsonc(path, new_config)
            print(f"Normalized {len(changes)} entry(ies): {', '.join(changes)}")
        else:
            print("No normalization needed (already in canonical format).")

        if new_issues:
            print(f"\nRemaining issues that need manual fix ({len(new_issues)}):")
            for issue in new_issues:
                print(f"  - {issue}")
            return 1
        return 0

    # Default: --check mode
    if not issues:
        print(f"OK: {path} is canonical (no format issues).")
        return 0

    print(f"Found {len(issues)} issue(s) in {path}:")
    for issue in issues:
        print(f"  - {issue}")
    print(f"\nRun 'scripts/lint-omo-config.py --fix {path}' to auto-convert.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
