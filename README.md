# OpenCode Configuration

This repository contains OpenCode AI agent configurations optimized for speed, reasoning quality, and cost efficiency.

## Files

| File | Purpose |
|------|---------|
| `oh-my-openagent.jsonc` | Main agent configuration (16 agents, categories, routing) |
| `opencode.json` | Core provider settings, default Kimi K3 model, Chenco Qwen3.6 models, MiniMax token-plan models, and MiniMax PayGo fallback |
| `opencode-large-project.json` | Extended config for large projects |
| `zed-*.json` | Zed editor integration configs |
| `OPENCODE_MANUAL.md` | Complete usage guide |

## Setup

### 1. Clone and install

```bash
# Clone to your config directory
git clone <your-repo-url> ~/.config/opencode

# Or create symlink
ln -s ~/your-repo-path ~/.config/opencode
```

### 2. Add your API keys (NOT in git!)

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

### 2b. n8n-mcp (optional)

The `n8n-mcp` MCP server is configured in `opencode.json` but **disabled by default** to keep context lean. To enable:

1. Set `N8N_API_URL` and `N8N_API_KEY` in `.env.local` (see above).
2. In `opencode.json`, change `"enabled": false` to `"enabled": true` under `mcp.n8n-mcp`.
3. Reference its tools in prompts with the `n8n-mcp_*` prefix, e.g. *"use n8n-mcp to list my workflows"*.

Adds ~20 tools (workflow mgmt, executions, node docs, templates) plus a ~540MB node DB cache in `~/.config/opencode/data/`.

### 3. Start using

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
| Deep analysis | `@oracle` | Kimi K3 | ~8s |
| Architecture | `@prometheus` | Kimi K3 with MiniMax fallback | ~8-10s |

### Cost Optimization

- Kimi K3 is the default model for primary coding work and deep reasoning
- Kimi K2.7 provides a balanced, high-speed reasoning option
- MiniMax M2.7 Highspeed uses the token-plan key and is configured as OpenCode's fast/small model
- MiniMax M3 is the multi-modal fallback and orchestration model
- MiniMax PayGo is exposed as `minimax-paygo/MiniMax-M2.7-highspeed` and is only used after token-plan MiniMax fails
- MiniMax token-plan routing handles utility tasks and lightweight plan coordination
- Kimi K3/K2.7 reasoning remains reserved for strategic planning, deep refactors, visual reasoning, critique, and hard debugging
- Runtime fallback escalates stalled or quota-limited Kimi requests after 30 seconds
- Category routing sets per-task `variant`/`thinking` and `maxTokens` budgets

## Customization

Edit `oh-my-openagent.jsonc` to adjust:
- Agent models and token limits
- Category routing rules
- Parallel execution limits
- Auto-confirmation settings

See `OPENCODE_MANUAL.md` for full documentation.

## License

Personal configuration - adjust as needed for your workflow.
