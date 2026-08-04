#!/usr/bin/env python3
"""Upgrade omo.jsonc agent entries from the deprecated `model + fallback_models`
schema to the plugin's current `models:[{primary}, ...fallbacks]` schema.

WHY THIS EXISTS
===============
oh-my-openagent@4.19.4's runtime schema (OmoAgentDefInputSchema, .strict())
rejects `fallback_models` as an unknown key. When an agent entry fails to
parse, the plugin silently falls back to its built-in defaults — which for
`deep` is `gpt-5.6-sol` and for `artistry` is `claude-fable-5`. Those models
are not configured in this setup, so tasks routed to those categories fail
or misbehave.

The plugin's `config migrate` command only handles the pre-omo.jsonc era
(oh-my-openagent.jsonc -> ~/.omo/omo.jsonc). It does NOT fix this in-place
schema drift. So a script is needed.

WHAT IT DOES
============
For every agent entry under [opencode].agents:
  - Drop `model` (singular) and `fallback_models` keys
  - Build a models:[ ... ] array
  - Put per-model options (reasoning, variant, reasoningEffort) on the
    primary model object
  - Translate `thinking: { type: enabled }` (K2.7) into
    `provider_options.thinking: { type: enabled }` on the primary slot
  - Translate `thinking: { type: adaptive }` (M3, never valid but seen in
    older configs) into `reasoning: auto` on the primary slot
  - Preserve all other agent-level keys (mode, displayName, prompt, tools,
    temperature, etc.)

Idempotency:
  - If an agent already has `models:[]` with no `model`/`fallback_models`,
    it is left untouched
  - If a migration marker is already in `_migrations`, the script still
    re-validates but does not duplicate work

WHAT IT DOES NOT DO
===================
  - Touch categories (they are already in models:[] format)
  - Touch the live ~/.omo/omo.jsonc directly (run sync-omo.sh push/pull
    yourself, or edit the repo copy and let the workflow handle it)
  - Validate against the actual zod schema (this script is a structural
    rewrite, not a schema check)
"""
import argparse
import json
import re
import sys
from pathlib import Path


def strip_jsonc_comments(text: str) -> str:
    return re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)


def load_jsonc(path: Path) -> dict:
    raw = strip_jsonc_comments(path.read_text())
    raw = re.sub(r",(\s*[}\]])", r"\1", raw)
    return json.loads(raw)


def write_jsonc(path: Path, data: dict) -> None:
    raw = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text("// OMO configuration\n" + raw + "\n")


def convert_agent(agent_def: dict) -> tuple[dict, bool]:
    """Convert a single agent entry. Returns (new_def, changed)."""
    primary = agent_def.get("model")
    fallbacks = agent_def.get("fallback_models")
    has_legacy = primary is not None or fallbacks is not None

    if not has_legacy and "models" in agent_def:
        return dict(agent_def), False

    primary_obj: dict = {}
    if isinstance(primary, str):
        primary_obj["model"] = primary

    for key in ("reasoning", "variant", "reasoningEffort"):
        v = agent_def.get(key)
        if v is not None:
            primary_obj[key] = v

    thinking = agent_def.get("thinking")
    if isinstance(thinking, dict):
        ttype = thinking.get("type")
        if ttype == "enabled":
            primary_obj.setdefault("provider_options", {})["thinking"] = thinking
        elif ttype == "adaptive":
            primary_obj["reasoning"] = "auto"
        elif ttype == "disabled":
            primary_obj["reasoning"] = "off"

    new_def = {
        k: v
        for k, v in agent_def.items()
        if k not in {
            "model", "fallback_models",
            "reasoning", "variant", "reasoningEffort",
            "thinking",
        }
    }
    new_def["models"] = ([primary_obj] if primary_obj else []) + list(fallbacks or [])
    return new_def, True


def upgrade_config(cfg: dict) -> tuple[dict, list[str]]:
    """Return (new_config, list_of_changes)."""
    opencode = cfg.get("[opencode]", {})
    agents = opencode.get("agents", {})
    changes: list[str] = []

    converted: dict[str, dict] = {}
    for name, defn in agents.items():
        new_defn, changed = convert_agent(defn)
        converted[name] = new_defn
        if changed:
            changes.append(name)

    opencode["agents"] = converted

    migrations = cfg.get("_migrations", [])
    marker = "2026-08-agent-models-array-conversion"
    if marker not in migrations:
        migrations.append(marker)
    cfg["_migrations"] = migrations

    return cfg, changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "path",
        nargs="?",
        default="omo.jsonc",
        help="Path to omo.jsonc (default: ./omo.jsonc)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only report what would change; do not write the file",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1

    cfg = load_jsonc(path)
    new_cfg, changes = upgrade_config(cfg)

    if not changes:
        print("No changes needed (already in models:[] format).")
        return 0

    print(f"Would convert {len(changes)} agent(s): {', '.join(changes)}")
    if args.check:
        return 0

    write_jsonc(path, new_cfg)
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())