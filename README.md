# OpenCode Configuration

This repository contains OpenCode AI agent configurations optimized for speed and cost efficiency.

## Files

| File | Purpose |
|------|---------|
| `oh-my-opencode.json` | Main agent configuration (16 agents, categories, routing) |
| `opencode.json` | Core provider settings (Kimi + OpenCode Go) |
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
# OpenCode Go
OPENCODE_GO_API_KEY=your_actual_key_here

# Kimi (if needed)
KIMI_API_KEY=your_actual_key_here
```

Or use environment variables:

```bash
export OPENCODE_GO_API_KEY="your_key"
export KIMI_API_KEY="your_key"
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
| Search/Grep | `@explore` | MiniMax | ~1s |
| Quick fixes | `@fixer` | MiniMax | ~1s |
| Deep analysis | `@oracle` | Kimi | ~8s |
| Architecture | `@prometheus` | Kimi | ~10s |

### Cost Optimization

- 70% MiniMax (fast & cheap) - 100K req/month
- 25% Kimi (powerful) - 9K req/month typical
- Parallel execution enabled (12 concurrent agents)

## Customization

Edit `oh-my-opencode.json` to adjust:
- Agent models and token limits
- Category routing rules
- Parallel execution limits
- Auto-confirmation settings

See `OPENCODE_MANUAL.md` for full documentation.

## License

Personal configuration - adjust as needed for your workflow.
