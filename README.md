# OpenCode Configuration

This repository contains OpenCode AI agent configurations optimized for speed, reasoning quality, and cost efficiency.

## Files

| File | Purpose |
|------|---------|
| `omo.jsonc` | Main agent configuration (agents, categories, routing) - unified OMO schema, lives at `~/.omo/omo.jsonc` via symlink |
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

### 2. Link the agent config (omo.jsonc)

Since oh-my-openagent 4.19.x, the plugin config lives at `~/.omo/omo.jsonc`
(the plugin auto-migrates legacy `oh-my-openagent.json[c]` there on first
launch). This repo keeps the real file under version control and links it:

```bash
mkdir -p ~/.omo
# If the plugin already migrated/created one, back it up first:
[ -f ~/.omo/omo.jsonc ] && [ ! -L ~/.omo/omo.jsonc ] && mv ~/.omo/omo.jsonc ~/.omo/omo.jsonc.pre-symlink
ln -sf ~/.config/opencode/omo.jsonc ~/.omo/omo.jsonc

# Verify the full agent roster loads through the link:
opencode agent list
```

**Do NOT** recreate `oh-my-openagent.json[c]` in `~/.config/opencode/` - the
plugin's config migration will detect it and re-run, overwriting the symlink
setup. Edit `omo.jsonc` (in this repo) directly; the plugin reads and writes
through the symlink. Pre-migration backups live under
`~/.omo/migration-backup-*` and `~/.omo/omo.jsonc.pre-symlink`.

### 3. Add your API keys (NOT in git!)

Create `~/.config/opencode/.env.local`:

```bash
# Kimi (if needed)
KIMI_API_KEY=your_actual_key_here

# MiniMax token plan
MINIMAX_API_KEY=your_actual_key_here

# MiniMax PayGo fallback
MINIMAX_PAYGO_API_KEY=your_actual_key_here

# Chenco OpenAI-compatible endpoint
CHENCO_API_KEY=your_actual_key_here

# n8n-mcp (optional, only if you use the n8n MCP server)
N8N_API_URL=https://your-n8n-instance.example.com
N8N_API_KEY=your_n8n_api_key_here
```

Or use environment variables:

```bash
export KIMI_API_KEY="your_key"
export MINIMAX_API_KEY="your_key"
export MINIMAX_PAYGO_API_KEY="your_key"
export CHENCO_API_KEY="your_key"
export N8N_API_URL="https://your-n8n-instance.example.com"
export N8N_API_KEY="your_key"
```

### 3b. n8n-mcp (optional)

The `n8n-mcp` MCP server is configured in `opencode.json` but **disabled by default** to keep context lean. To enable:

1. Set `N8N_API_URL` and `N8N_API_KEY` in `.env.local` (see above).
2. In `opencode.json`, change `"enabled": false` to `"enabled": true` under `mcp.n8n-mcp`.
3. Reference its tools in prompts with the `n8n-mcp_*` prefix, e.g. *"use n8n-mcp to list my workflows"*.

Adds ~20 tools (workflow mgmt, executions, node docs, templates) plus a ~540MB node DB cache in `~/.config/opencode/data/`.

### 4. Start using

```bash
opencode
```

## Security

- **No API keys in git** - Keys are injected via environment
- **Pattern-based .gitignore** - Prevents accidental commits of secrets
- `.env*` files are ignored
- `*secret*`, `*credential*`, `*key*` patterns blocked

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

Edit `omo.jsonc` (in this repo; live at `~/.omo/omo.jsonc` via symlink) to adjust:
- Agent models and token limits (unified `models[]` arrays - first entry is primary, rest are fallbacks)
- Category routing rules
- Parallel execution limits
- Auto-confirmation settings

See `OPENCODE_MANUAL.md` for full documentation.

## License

Personal configuration - adjust as needed for your workflow.
