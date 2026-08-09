# Scripts

Operational scripts for keeping this repo in sync with the live
`~/.omo/omo.jsonc` and for keeping the omo config in canonical format.

## sync-omo.sh

Bidirectional sync between the version-controlled `omo.jsonc` (this repo)
and the live plugin config at `~/.omo/omo.jsonc`.

```bash
scripts/sync-omo.sh push      # repo  -> ~/.omo/omo.jsonc
scripts/sync-omo.sh pull      # ~/.omo/omo.jsonc -> repo
scripts/sync-omo.sh check     # diff the two, exit 1 if they differ
scripts/sync-omo.sh validate  # run scripts/lint-omo-config.py
scripts/sync-omo.sh doctor    # JSONC check + format lint + plugin doctor + agent roster
```

Use `push` after editing the repo copy. Use `pull` after the plugin
auto-migrates or rewrites its config. `check` should be wired into CI or
run before any commit.

`push` and `check` run the format linter first and refuse to proceed
if `omo.jsonc` has any format issues — this prevents pushing a broken
config that the plugin's runtime would silently fall back to defaults
for. Use `validate` or `lint-omo-config.py` directly to see what's wrong.

## lint-omo-config.py

The plugin's runtime schema only extracts `model`, `fallback_models`,
`variant`, `thinking`, etc. from agents and categories. The `models:[]`
array is **dropped** — the runtime falls back to the plugin's built-in
defaults (e.g. `claude-fable-5`, `gpt-5.6-sol`, `kimi-for-coding-highspeed`).

This linter enforces the canonical `model + fallback_models` form for
both agents and categories, so the plugin runtime always uses the
user's config rather than silently substituting defaults.

```bash
scripts/lint-omo-config.py              # check current omo.jsonc
scripts/lint-omo-config.py --check     # same as default (no writes)
scripts/lint-omo-config.py --fix       # auto-convert to canonical
scripts/lint-omo-config.py path/to/file  # lint a specific file
```

Exit codes:
- `0` — no issues (or issues fixed with `--fix`)
- `1` — issues found (run `--fix` or fix manually)
- `2` — parse error / file not found

The linter also catches:
- Empty `model` strings
- Non-string fallback entries
- Invalid `reasoning` values (must be one of `off | minimal | low | medium | high | xhigh | max | auto`)
- Invalid `thinking.type` values (must be `enabled` or `disabled`)

## revert-agent-schema.py

Backward-compatible wrapper around `lint-omo-config.py --fix`. Kept for
older docs that reference this name. New code should call
`lint-omo-config.py` directly.

```bash
scripts/revert-agent-schema.py                  # auto-fix omo.jsonc
scripts/revert-agent-schema.py --check omo.jsonc  # report only
```

The original script only handled agents. The wrapper now delegates to
`lint-omo-config.py`, which handles both agents AND categories.

## Why the format matters

The plugin's `modelInput` function (in `cli-node/index.js`, around
line 104215) only extracts specific fields for categories:

```js
const fields = recordFields(definition, [
  "description", "model", "fallback_models", "variant",
  "temperature", "top_p", "maxTokens", "thinking",
  "reasoningEffort", "textVerbosity", "tools",
  "prompt_append", "max_prompt_tokens", "is_unstable_agent", "disable"
]);
```

Notably absent: `models`. If a category uses `models: [{...}]`, the
runtime strips it out and falls back to the plugin's
`CATEGORY_MODEL_REQUIREMENTS` defaults. This is why the user's
config might appear to be working (JSONC valid, schema valid) but
the plugin silently uses models like `claude-fable-5` or
`gpt-5.6-sol` instead of the configured `glm-5.2` or `qwen3.8-max`.

The lint+fix combo keeps this from happening silently.

### Historical note

Older docs (and the original `revert-agent-schema.py` docstring) claimed
that categories "correctly use `models:[]`" while agents use the legacy
`model + fallback_models` form. This was wrong — the plugin's runtime
drops `models:[]` for categories too, so they need the same legacy
form as agents. The lint+fix tooling reflects the correct behavior.

## When `oh-my-opencode doctor` says "Configuration invalid"

You are probably seeing this after a hand-edit or plugin auto-migration
moved an agent into `models:[]` form. Two options:

1. **Run `scripts/lint-omo-config.py --fix omo.jsonc`** to put it back
   to the legacy form. This is the recommended fix.

2. **Move the agent definitions to top-level `agents`** (no `[opencode]`
   wrapper). The top-level `agents` uses strict `OmoAgentsConfigSchema`,
   which DOES accept `models:[]`. But this breaks opencode harness
   routing and is not recommended.

If neither works, the plugin version has likely drifted past what this
config supports. Pin the plugin version or open an issue upstream.

## Recommended workflow

```bash
# 1. Edit omo.jsonc (model + fallback_models form)
vim omo.jsonc

# 2. Verify format
scripts/sync-omo.sh validate

# 3. Push to live config
scripts/sync-omo.sh push

# 4. Run doctor for full health check
scripts/sync-omo.sh doctor
```

The plugin reads the live config at session start, so push is sufficient
to apply changes for the next session.
