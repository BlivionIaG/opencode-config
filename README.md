# OpenCode Configuration

This repository contains OpenCode AI agent configurations optimized for speed and cost efficiency.

## Files

| File | Purpose |
|------|---------|
| `oh-my-openagent.json` | Main agent configuration (16 agents, categories, routing) |
| `opencode.json` | Core provider settings, default Kimi K2.6 model, Chenco Qwen3.6 models, MiniMax token-plan model, and MiniMax PayGo fallback |
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
```

Or use environment variables:

```bash
export KIMI_API_KEY="your_key"
export MINIMAX_API_KEY="your_key"
export MINIMAX_PAYGO_API_KEY="your_key"
export CHENCO_API_KEY="your_key"
```

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
| Search/Grep | `@explore` | MiniMax instant | ~1-2s |
| Quick fixes | quick/fix category | MiniMax instant | ~1-2s |
| Deep analysis | `@oracle` | Kimi thinking | ~8s |
| Architecture | `@prometheus` | Kimi thinking with MiniMax fallback | ~8-10s |

### Cost Optimization

- Kimi K2.6 remains the main model for primary coding work
- MiniMax M2.7 Highspeed uses the token-plan key and is configured as OpenCode's fast/small model
- MiniMax PayGo is exposed as `minimax-paygo/MiniMax-M2.7-highspeed` and is only used after token-plan MiniMax fails
- MiniMax token-plan routing handles utility tasks and lightweight plan coordination
- Kimi thinking mode remains reserved for strategic planning, deep refactors, visual reasoning, critique, and hard debugging
- Runtime fallback escalates stalled or quota-limited Kimi requests after 30 seconds
- Category routing sets per-task `thinking` and `maxTokens` budgets

## Customization

Edit `oh-my-openagent.json` to adjust:
- Agent models and token limits
- Category routing rules
- Parallel execution limits
- Auto-confirmation settings

See `OPENCODE_MANUAL.md` for full documentation.

## License

Personal configuration - adjust as needed for your workflow.
