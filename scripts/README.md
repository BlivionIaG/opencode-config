# Scripts

Operational scripts for keeping this repo in sync with the live
`~/.omo/omo.jsonc` and for one-shot schema upgrades.

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

## upgrade-agent-schema.py

Idempotent one-shot converter that rewrites agent entries from the
deprecated `model + fallback_models` schema to the plugin's current
`models:[{primary}, ...fallbacks]` schema.

**When to run it:** if `oh-my-opencode doctor` reports
`Deprecated reasoning config key ... fallback_models` warnings, or if a
category that should use your custom models is silently falling back to
plugin built-in defaults (e.g. `gpt-5.6-sol`, `claude-fable-5`).

```bash
# Preview what would change (no file writes):
scripts/upgrade-agent-schema.py --check omo.jsonc

# Apply the conversion:
scripts/upgrade-agent-schema.py omo.jsonc
```

The script is idempotent — re-running it on an already-converted config
reports `No changes needed`. After running:

```bash
scripts/sync-omo.sh push    # ship the converted config to ~/.omo/
scripts/sync-omo.sh doctor  # verify doctor is happy
```

### What it does

For every agent under `[opencode].agents`:

| Legacy key                                       | Action                                                              |
| ------------------------------------------------ | ------------------------------------------------------------------- |
| `model` + `fallback_models`                      | Folded into `models:[{primary_obj}, ...fallbacks]`                  |
| `reasoning` / `variant` / `reasoningEffort`      | Moved onto the primary model object                                 |
| `thinking: { type: enabled }` (K2.7)             | Moved to `provider_options.thinking: { type: enabled }` on primary  |
| `thinking: { type: adaptive }` (M3, was invalid)  | Translated to `reasoning: "auto"` on primary                        |
| `thinking: { type: disabled }`                   | Translated to `reasoning: "off"` on primary                         |
| Other keys (mode, displayName, prompt, tools…)   | Preserved                                                           |

### What it does NOT do

- Touch categories — they're already in `models:[]` format
- Touch the live `~/.omo/omo.jsonc` directly — use `sync-omo.sh push`
- Validate against the plugin's zod schema — this is a structural rewrite,
  not a semantic check. Use `sync-omo.sh doctor` for validation.

## When the doctor complains about `models` being unknown

After running this converter, `oh-my-opencode doctor` may still report
`Invalid configuration / Unknown config key: agents.{name}.models` for
each agent. This is a **false positive**: the doctor uses an older schema
(`OhMyOpenCodeConfigSchema`) that predates the plugin's runtime schema
(`OmoAgentDefSchema`), which does accept `models:[]` on agents. The
runtime honors the converted config correctly; the doctor complaints will
go away when the plugin's doctor schema is updated.

If you actually want to silence the doctor, the only options are:

1. Wait for the plugin to ship a doctor schema update.
2. Move the agents into a `models`-only top-level config (no harness
   block) — but that breaks the opencode harness routing and is not
   recommended.
3. Live with the warnings (recommended) — they're cosmetic.