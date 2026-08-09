# OpenCode Configuration

This repository contains OpenCode AI agent configurations optimized for speed, reasoning quality, and cost efficiency.

## Files

| File | Purpose |
|------|---------|
| `omo.jsonc` | Main agent configuration (agents, categories, routing) - unified OMO schema, synced to `~/.omo/omo.jsonc` |
| `scripts/sync-omo.sh` | Syncs repo `omo.jsonc` with the live plugin config (push/pull/check/doctor) |
| `opencode.json` | Core provider settings, default MiniMax M3 model, Chenco Qwen3.6 models, MiniMax models, native agents (`vulcan`) |
| `agents/vulcan.md` | System prompt for the Vulcan deep-worker agent (Kimi K3, 1M context) |
| `OPENCODE_MANUAL.md` | Complete usage guide |

## Setup

### 1. Clone and install

```bash
# Clone to your config directory
git clone <your-repo-url> ~/.config/opencode

# Or create symlink
ln -s ~/your-repo-path ~/.config/opencode
```

### 2. Install the agent config (omo.jsonc)

Since oh-my-openagent 4.19.x, the plugin config lives at `~/.omo/omo.jsonc`
(the plugin auto-migrates legacy `oh-my-openagent.json[c]` there on first
launch). This repo keeps the canonical copy under version control and syncs
it with a script:

```bash
# Install / update the live config from this repo:
scripts/sync-omo.sh push

# Verify everything is wired up (JSONC check + plugin doctor + agent roster):
scripts/sync-omo.sh doctor
```

Day-to-day workflow:

| Situation | Command |
|-----------|---------|
| You edited `omo.jsonc` in the repo | `scripts/sync-omo.sh push` |
| The plugin migrated/wrote its config (e.g. after an upgrade) | `scripts/sync-omo.sh pull` then review `git diff` |
| Not sure which side is newer | `scripts/sync-omo.sh check` |

We deliberately do **not** symlink `~/.omo/omo.jsonc`: the plugin's config
migration can rewrite that path, and a symlink breaks silently. Copies +
`sync-omo.sh check` make drift visible instead.

**Do NOT** recreate `oh-my-openagent.json[c]` in `~/.config/opencode/` - the
plugin's config migration will detect it and re-run. Pre-migration backups
live under `~/.omo/migration-backup-*`; the sync script also timestamps its
own backups on push.

### 3. Add your API keys (NOT in git!)

Add the keys to your shell config so every process inherits them. Pick the file that matches your shell:

- **zsh** → `~/.zshenv` (loaded for every zsh invocation, including non-interactive scripts)
- **bash** → `~/.bashrc` (interactive) or `~/.bash_profile` (login shells)
- **fish** → `~/.config/fish/config.fish` (using `set -x KEY value`)

```bash
# Kimi (if needed)
export KIMI_API_KEY="your_actual_key_here"

# MiniMax token plan
export MINIMAX_API_KEY="your_actual_key_here"

# MiniMax PayGo fallback
export MINIMAX_PAYGO_API_KEY="your_actual_key_here"

# Chenco OpenAI-compatible endpoint
export CHENCO_API_KEY="your_actual_key_here"

# Alibaba Cloud Model Studio (bailian token plan, Anthropic-compatible)
export BAILIAN_TOKEN_PLAN_API_KEY="your_actual_key_here"

# n8n-mcp (optional, only if you use the n8n MCP server)
export N8N_API_URL="https://your-n8n-instance.example.com"
export N8N_API_KEY="your_n8n_api_key_here"
```

Then reload the file (e.g. `source ~/.zshenv`) or restart your shell.

`opencode.json` references these via `{env:VAR_NAME}` placeholders, so the provider config stays secret-free.

### 3b. n8n-mcp (optional)

The `n8n-mcp` MCP server is configured in `opencode.json` but **disabled by default** to keep context lean. To enable:

1. Set `N8N_API_URL` and `N8N_API_KEY` in your shell config (see above).
2. In `opencode.json`, change `"enabled": false` to `"enabled": true` under `mcp.n8n-mcp`.
3. Reference its tools in prompts with the `n8n-mcp_*` prefix, e.g. *"use n8n-mcp to list my failing workflows"*.

Adds ~20 tools (workflow mgmt, executions, node docs, templates) plus a ~540MB node DB cache in `~/.config/opencode/data/`.

### 4. Start using

```bash
opencode
```

## Security

- **No API keys in git** - Keys live in your shell config (`~/.zshenv`, `~/.bashrc`, etc.), outside the repo
- **Defense-in-depth .gitignore** - Even if a `.env` file slips in, the pattern blocks `.env*`, `*secret*`, `*credential*`, `*key*` from being committed

## Architecture

### Agent Routing

| Task Type | Agent | Model | Speed |
|-----------|-------|-------|-------|
| Search/Grep | `@explore` | MiniMax M2.7 highspeed | ~1-2s |
| Quick fixes | quick/fix category | MiniMax M2.7 highspeed | ~1-2s |
| Deep analysis | `@oracle` | Kimi K3-256k | ~8s |
| Architecture | `@prometheus` | Kimi K3-256k | ~8-10s |
| Long-horizon implementation | `@vulcan` | Kimi K3 (1M) | varies |

### Cost Optimization

- MiniMax M3 is the default session model (orchestration is cheap delegation, not deep reasoning)
- Kimi K3-256k handles K3-quality reasoning (oracle, prometheus, ultrabrain, visual-engineering) at half the quota of K3 1M
- Kimi K3 1M is reserved for long-horizon work (`@vulcan`, `deep` category) and video input (`multimodal-looker`)
- Kimi K2.7 provides a balanced, high-speed reasoning option
- MiniMax M2.7 Highspeed uses the token-plan key and is configured as OpenCode's fast/small model
- MiniMax PayGo is exposed as `minimax-paygo/MiniMax-M2.7-highspeed` and is only used after token-plan MiniMax fails
- Runtime fallback escalates stalled or quota-limited Kimi requests after 30 seconds
- Category routing sets per-task `variant`/`thinking` and `maxTokens` budgets

## Customization

Edit `omo.jsonc` (in this repo, then `scripts/sync-omo.sh push`) to adjust:
- Agent models and token limits (`model` + `fallback_models`; `reasoning`/`variant`/`thinking` per agent)
- Category routing rules (`models[]` arrays - first entry is primary, rest are fallbacks)
- Parallel execution limits
- Auto-confirmation settings

See `OPENCODE_MANUAL.md` for full documentation.

## License

Personal configuration - adjust as needed for your workflow.
