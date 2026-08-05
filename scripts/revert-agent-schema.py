#!/usr/bin/env python3
"""Revert agent entries from models:[] back to model + fallback_models.

WHY
===
The plugin's runtime schema (`OmoAgentDefSchema`, used at top-level under
`OmoConfigSchema.agents`) accepts `models:[]` but rejects `fallback_models`
in strict mode. So in theory `models:[]` is the modern form.

BUT — agents in this config live under `[opencode]`, which uses the
PERMISSIVE `OmoOpenCodeHarnessConfigSchema = record(string, unknown())`.
Under that schema, `model + fallback_models` is accepted without strict
validation, and the runtime's `normalizeDefinition` (called downstream)
collapses `model + fallback_models` into `models:[]` for actual use.

The plugin's DOCTOR uses a different, older schema
(`AgentOverrideConfigSchema`) for agent overrides. That schema:
  - accepts `fallback_models` (good for the runtime's permissive path)
  - does NOT accept `models` (so the doctor flags `models:[]` as
    "Unknown config key" → status: fail → "Configuration invalid")

So the only format that satisfies BOTH the runtime (under [opencode])
AND the doctor is the legacy `model + fallback_models` form. The doctor
will still emit "Deprecated reasoning config key" warnings
(see `CANONICAL_REPLACEMENT` in the plugin source), but those are
cosmetic (status: warn, not fail) — they do not block plugin startup.

WHAT IT DOES
============
For every agent entry under [opencode].agents:
  - If the entry uses `models:[]`, fold it back into `model + fallback_models`
  - Move per-model `reasoning`, `variant`, `reasoningEffort` from the
    primary slot back onto the agent level
  - Translate primary-slot `provider_options.thinking` (K2.7) back to
    agent-level `thinking: { type: enabled }`
  - Translate primary-slot `reasoning: "auto"` (M3 adaptive) back to
    agent-level `thinking: { type: adaptive }` (legacy equivalent that
    normalizeDefinition still understands)

Idempotent:
  - If an agent already has `model + fallback_models`, it is left untouched
  - If an agent already has neither (just `models:[]`), it is converted
  - Re-running on already-reverted config reports "No changes needed"

WHAT IT DOES NOT DO
===================
  - Touch categories (they correctly use `models:[]` and the doctor
    accepts that for `CategoryConfigSchema`)
  - Touch the live ~/.omo/omo.jsonc directly — use `sync-omo.sh push`
  - Validate against the actual zod schemas (structural rewrite only)
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


def revert_agent(agent_def: dict) -> tuple[dict, bool]:
    """Convert an agent entry back to model + fallback_models. Returns
    (new_def, changed)."""
    if "model" in agent_def and "fallback_models" in agent_def:
        return dict(agent_def), False

    models = agent_def.get("models")
    if not models:
        return dict(agent_def), False

    primary = models[0]
    fallbacks = list(models[1:])

    new_def = {k: v for k, v in agent_def.items() if k != "models"}

    if isinstance(primary, dict):
        model_name = primary.get("model")
        if model_name is None:
            raise ValueError(f"agent primary slot missing 'model': {primary!r}")
        new_def["model"] = model_name
        for key in ("reasoning", "variant", "reasoningEffort"):
            if key in primary:
                new_def[key] = primary[key]
        provider_options = primary.get("provider_options", {})
        thinking = provider_options.get("thinking") if isinstance(provider_options, dict) else None
        if isinstance(thinking, dict) and thinking.get("type") == "enabled":
            new_def["thinking"] = thinking
        if primary.get("reasoning") == "auto":
            new_def["reasoning"] = "auto"
    elif isinstance(primary, str):
        new_def["model"] = primary
    else:
        raise ValueError(f"unexpected primary slot type: {type(primary).__name__}")

    new_def["fallback_models"] = fallbacks
    return new_def, True


def revert_config(cfg: dict) -> tuple[dict, list[str]]:
    opencode = cfg.get("[opencode]", {})
    agents = opencode.get("agents", {})
    changes: list[str] = []
    converted: dict[str, dict] = {}
    for name, defn in agents.items():
        new_defn, changed = revert_agent(defn)
        converted[name] = new_defn
        if changed:
            changes.append(name)
    opencode["agents"] = converted
    return cfg, changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("path", nargs="?", default="omo.jsonc")
    parser.add_argument("--check", action="store_true",
                        help="Only report what would change; do not write")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1

    cfg = load_jsonc(path)
    new_cfg, changes = revert_config(cfg)

    if not changes:
        print("No changes needed (already in model + fallback_models format).")
        return 0

    print(f"Would revert {len(changes)} agent(s): {', '.join(changes)}")
    if args.check:
        return 0

    write_jsonc(path, new_cfg)
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())