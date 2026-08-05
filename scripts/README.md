# Scripts

Operational scripts for keeping this repo in sync with the live
`~/.omo/omo.jsonc` and for one-shot schema migrations.

## sync-omo.sh

Bidirectional sync between the version-controlled `omo.jsonc` (this repo)
and the live plugin config at `~/.omo/omo.jsonc`.

```bash
scripts/sync-omo.sh push    # repo  -> ~/.omo/omo.jsonc
scripts/sync-omo.sh pull    # ~/.omo/omo.jsonc -> repo
scripts/sync-omo.sh check   # diff the two, exit 1 if they differ
scripts/sync-omo.sh doctor  # JSONC check + plugin doctor + agent roster
```

Use `push` after editing the repo copy. Use `pull` after the plugin
auto-migrates or rewrites its config. `check` should be wired into CI or
run before any commit.

## revert-agent-schema.py

The agent schema in this repo uses the **legacy** `model + fallback_models`
form on purpose — see "Why legacy format?" below. If you accidentally
hand-edit an agent to use the modern `models:[]` array form, or if the
plugin's auto-migration rewrites one, this script converts it back.

```bash
# Preview what would change (no file writes):
scripts/revert-agent-schema.py --check omo.jsonc

# Apply the conversion:
scripts/revert-agent-schema.py omo.jsonc
```

The script is idempotent — re-running on already-reverted config reports
`No changes needed`. It only touches `[opencode].agents.*`; categories
(which legitimately use `models:[]`) are left alone.

### Why legacy format?

The plugin has two different schemas for agents:

| Schema                              | Where used                              | Accepts                  |
| ----------------------------------- | --------------------------------------- | ------------------------ |
| `AgentOverrideConfigSchema`         | `oh-my-opencode doctor`                 | `model + fallback_models`|
| `OmoAgentDefSchema` (`.strict()`)   | `OmoConfigSchema.agents` (top-level)    | `models:[]` array        |

This repo puts agents under `[opencode].agents`, which uses the
**permissive** `OmoOpenCodeHarnessConfigSchema = record(string, unknown())`.
That schema accepts `model + fallback_models` without strict validation,
and the runtime's `normalizeDefinition` step collapses that form into
`models:[]` for actual use downstream.

If you switch to `models:[]` here, two things break:

1. The doctor (which uses `AgentOverrideConfigSchema`) reports every
   `agents.{name}.models` as `Invalid configuration / Unknown config key`
   with `severity: error`, `affects: plugin startup`. The config check
   status flips to `fail`. The doctor warning stops being cosmetic.
2. The plugin's runtime still works because `[opencode]` is permissive,
   but you get a constant `Config invalid` banner every time you open a
   session.

The current convention is therefore:

- **Agents** (`[opencode].agents.*`): legacy `model + fallback_models`
- **Categories** (`[opencode].categories.*`): modern `models:[]`

The doctor emits "Deprecated reasoning config key" warnings on agents for
`fallback_models` and `thinking`. Those are warnings (status `warn`), not
errors — `replace with models` is the plugin's suggested migration but
the doctor schema has not been updated to match. The runtime handles
both forms under `[opencode]` correctly.

## When `oh-my-opencode doctor` says "Configuration invalid"

You are probably seeing this after a hand-edit or plugin auto-migration
moved an agent into `models:[]` form. Two options:

1. **Run revert-agent-schema.py** to put it back to the legacy form.
   This is the recommended fix.

2. **Move the agent definitions to top-level `agents`** (no `[opencode]`
   wrapper). The top-level `agents` uses strict `OmoAgentsConfigSchema`,
   which DOES accept `models:[]`. But this breaks opencode harness
   routing and is not recommended.

If neither works, the plugin version has likely drifted past what this
config supports. Pin the plugin version or open an issue upstream.