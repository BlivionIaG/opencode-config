# OpenCode Setup Manual

**Version:** 1.0  
**Last Updated:** 2026-04-01  
**Subscriptions:** Kimi Code

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Your Configuration](#your-configuration)
3. [Agents Guide](#agents-guide)
4. [Categories & Smart Routing](#categories--smart-routing)
5. [Parallel Workflows](#parallel-workflows)
6. [Cost Optimization](#cost-optimization)
7. [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Start OpenCode

```bash
# Navigate to project
cd ~/my-project

# Start OpenCode
opencode

# Or with initial task
opencode "Your task here"
```

### Essential Commands

| Command | Description |
|---------|-------------|
| `@explore <task>` | Fast search (Kimi instant, ~2s) |
| `@oracle <task>` | Deep analysis (Kimi thinking, ~8s) |
| `@librarian <task>` | Docs and external reference lookup (Kimi instant, ~3s) |
| `@plan <task>` | Implementation planning (Kimi thinking, ~8s) |
| `agent1 & agent2` | Run agents in parallel |
| `/status` | Check running agents |
| `/models` | Switch models manually |
| `Ctrl+C` | Cancel current task |

### Provider Rate Limits

| Provider | Requests/min | Concurrent |
|----------|--------------|------------|
| Kimi Code | 40 | 4 |
| MiniMax | Account-dependent | Account-dependent |
| Chenco | Account-dependent | Account-dependent |

---

## Your Configuration

### Enabled Providers

1. **kimi-for-coding** - Kimi K2.6 (powerful reasoning, 256K context)
2. **minimax** - MiniMax M2.7 Highspeed (fast/small model, 200K context, 131K output)
3. **chenco** - Chenco OpenAI-compatible endpoint (Qwen3.6 model family)

### Model Characteristics

**Kimi K2.6 (kimi-for-coding/k2p6)**
- ✅ Deep reasoning, architecture, debugging
- ✅ Multimodal (vision + text)
- ✅ 256K context window
- ✅ Thinking and instant modes via `thinking.type`
- ⚠️ Slower, more expensive
- ⚠️ Leave sampling settings unset; K2.6 rejects non-default `temperature`, `top_p`, `n`, and penalties
- Use for: complex planning, debugging, visual tasks

**MiniMax M2.7 Highspeed (minimax/MiniMax-M2.7-highspeed)**
- ✅ Fast model configured as OpenCode `small_model`
- ✅ 204,800 context limit
- ✅ 131,072 output limit
- ✅ Tool-call capable in OpenCode's provider metadata
- ⚠️ Higher highspeed pricing than standard MiniMax M2.7
- Use for: quick/simple responses where latency matters

**Chenco Qwen3.6 Models**
- ✅ OpenAI-compatible LiteLLM endpoint
- ✅ API key loaded from `CHENCO_API_KEY`
- ✅ Available models: `chenco/qwen3.6-instruct`, `chenco/qwen3.6-coding`, `chenco/qwen3.6-agent`, `chenco/qwen3.6-vision`
- ⚠️ Limits and model capabilities depend on the Chenco gateway configuration
- Use for: manually selected Chenco-backed Qwen3.6 model runs

## Agents Guide

### Primary Agents

| Agent | Mode | Max Tokens | Use For |
|-------|------|------------|---------|
| **Sisyphus** | Kimi instant | 16384 | Main orchestrator, delegates tasks |
| **Atlas** | MiniMax instant | 16384 | Plan orchestration, task coordination with Kimi fallback |
| **Hephaestus** | Kimi thinking | 32768 | Deep autonomous work, research |
| **Prometheus** | Kimi thinking | 32768 | Strategic planning with MiniMax fallback |

### Utility Agents

| Agent | Mode | Max Tokens | Use For |
|-------|------|------------|---------|
| **Explore** | MiniMax instant | 8192 | Fast codebase grep, search |
| **Librarian** | MiniMax instant | 16384 | Documentation and external reference search |
| **Multimodal-Looker** | Kimi thinking | 32768 | Vision tasks, screenshots, UI analysis |
| **Sisyphus-Junior** | Category-based | 4096-32768 | Focused delegated task execution |

### Special Agents

| Agent | Mode | Max Tokens | Use For |
|-------|------|------------|---------|
| **Oracle** | Kimi thinking | 32768 | Architecture analysis, debugging |
| **Metis** | Kimi thinking | 32768 | Plan consulting |
| **Momus** | Kimi thinking | 32768 | Plan review |
| **Plan** | MiniMax thinking | 32768 | Work plan drafting with Kimi fallback |

### How to Use Agents

**Direct delegation:**
```bash
@explore find all TODO comments
@oracle analyze why tests are failing
@sisyphus fix the typo in README.md
```

**Parallel execution:**
```bash
# Run multiple agents simultaneously
@explore find auth files & @librarian search auth docs & @oracle review auth test strategy

# This completes in ~2 seconds instead of ~6 seconds
```

---

## Categories & Smart Routing

### Automatic Category Detection

Sisyphus automatically categorizes your requests based on keywords:

| Category | Trigger Keywords | Model | Speed |
|----------|-----------------|-------|-------|
| **quick** | fix, typo, rename, add import | MiniMax instant, 4096 maxTokens | ~1-2s |
| **search** | find, search, grep, locate | MiniMax instant, 4096 maxTokens | ~1-2s |
| **explain** | explain, what does, how to | MiniMax instant, 8192 maxTokens | ~2-3s |
| **test** | test, spec, validate | MiniMax instant, 8192 maxTokens | ~3-4s |
| **refactor** | refactor, cleanup, optimize | Kimi thinking, 32768 maxTokens | ~8s |
| **deep** | debug, investigate, analyze | Kimi thinking | ~8s |
| **ultrabrain** | architect, design, plan | Kimi thinking | ~10s |
| **visual-engineering** | UI, frontend, screenshot, design | Kimi thinking | ~8s |
| **writing** | write, document, describe | MiniMax instant, 8192 maxTokens | ~2-3s |
| **fix** | fix, correct, repair | MiniMax instant, 4096 maxTokens | ~1-2s |

### Examples

**Automatic instant routing (fast MiniMax, thinking disabled):**
```bash
"Find all console.log statements"           → @explore
"Add import for lodash"                      → @sisyphus-junior
"Fix typo in variable name"                  → quick/fix category
"Explain what this regex does"               → explain category
"Run tests for auth module"                  → test category
```

**Automatic quality routing (Kimi for strategic planning, hard debugging, and visual work):**
```bash
"Design a new authentication system"         → @prometheus
"Debug why the server crashes"               → @oracle
"Plan migration from REST to GraphQL"        → @prometheus
"Analyze architecture for scalability"       → @oracle
"Review this PR for security issues"         → @momus
```

### Manual Category Override

You can force a category by being explicit:
```bash
"Quick: find all TODOs"                      → Forces 'quick' category
"Deep analysis of performance"               → Forces 'deep' category
"Ultrabrain: design a caching layer"         → Forces 'ultrabrain' category
```

---

## Parallel Workflows

### Basic Parallelism

Use `&` to run agents simultaneously:

```bash
# 3 agents working in parallel
@explore find utils & @librarian search docs & @oracle validate approach

# Time: ~2 seconds total (vs ~6 seconds sequential)
```

### Common Parallel Patterns

**Pattern 1: Multi-file Search**
```bash
@explore find auth code & @explore find user code & @explore find session code
```

**Pattern 2: Code Review**
```bash
@explore find touched code & @oracle review architecture & @momus review plan quality
```

**Pattern 3: Research & Planning**
```bash
@librarian find examples & @explore find similar implementations & @oracle analyze approach
```

**Pattern 4: Testing**
```bash
@explore find related tests & @librarian check framework docs & @oracle review risky design
```

### Background Agents

Your config uses Kimi for quality-critical reasoning and MiniMax for fast utility work, with explicit instant/thinking settings per agent and category.

**Check status:**
```bash
/status
```

**Max parallel per provider:**
- Kimi: up to 4 agents simultaneously
- MiniMax: account-dependent

---

## Cost Optimization

### Cost Breakdown

| Operation | Model | Cost | Time |
|-----------|-------|------|------|
| Simple search | MiniMax instant | Lower Kimi quota use | ~1-2s |
| Quick fix | MiniMax instant | Lower Kimi quota use | ~1-2s |
| Code explanation | MiniMax instant | Lower Kimi quota use | ~2-3s |
| Test generation | MiniMax instant | Lower Kimi quota use | ~3-4s |
| Refactoring | Kimi thinking | Higher | ~8s |
| Deep analysis | Kimi | ~$0.005 | ~8s |
| Architecture planning | Kimi/MiniMax fallback | Higher | ~8-10s |

### Your Monthly Budget

**Kimi Code Subscription:**
- ~9,250 Kimi requests (typical usage)
- Rate limit: 40 req/min

**Typical Monthly Usage:**
- MiniMax for search, quick fixes, explanations, tests, writing, and lightweight plan coordination
- Thinking-mode Kimi for strategic planning, architecture, refactors, visual reasoning, critique, and hard debugging

### Cost-Saving Tips

✅ **DO:**
- Use simple language for simple tasks ("find X" → Kimi instant)
- Run independent tasks in parallel with `&`
- Trust automatic routing (it's optimized)
- Use `@explore` and `@librarian` for utility work
- Batch small operations (automatic batching enabled)

❌ **DON'T:**
- Use `@oracle` for "find this file" (wastes Kimi quota)
- Run everything sequentially (parallel is 3-4x faster)
- Force thinking mode for trivial tasks
- Request long outputs when short ones suffice

---

## Troubleshooting

### Common Issues

**Issue: Agent is slow**
```bash
# Check which model is being used
/status

# If using Kimi for simple tasks, that's the issue
# Let the system auto-route or use specific agent:
@explore find X    # Instead of deep analysis for search
```

**Issue: Rate limit hit**
```bash
# Wait 1 minute - limits reset automatically
# Or reduce concurrent agents in config from 12 to 8

# Edit oh-my-openagent.json:
"background_agents": {
  "max_concurrent": 8  # Reduced from 12
}
```

**Issue: Task fails**
```bash
# Confirm the resolved Kimi K2.6 config:
opencode debug config

# Check available Kimi models:
opencode models kimi-for-coding

# Check MiniMax fast model metadata:
opencode models minimax --verbose
```

**Issue: Wrong model selected**
```bash
# Override manually:
/models
# Select: kimi-for-coding/k2p6

# Fast/small model is configured as:
# minimax/MiniMax-M2.7-highspeed

# Or toggle thinking mode:
/acp thinking enabled   # Deep reasoning
/acp thinking disabled  # Fast mode
```

### Diagnostic Commands

```bash
# Check configuration health
bunx oh-my-opencode doctor

# Check current model
/models

# Check agent status
/status

# Check provider connections
/connection-status
```

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `opencode.json` | `~/.config/opencode/` | Provider settings |
| `oh-my-openagent.json` | `~/.config/opencode/` | Agent & category config |

### Reset Everything

```bash
# If you need to start fresh:
rm ~/.config/opencode/oh-my-openagent.json
cp ~/your-backup/oh-my-openagent.json ~/.config/opencode/

# Or regenerate:
bunx oh-my-opencode@latest install
```

---

## Advanced Usage

### Custom Categories

Add to `oh-my-openagent.json`:
```json
"categories": {
  "my-custom-category": {
    "model": "kimi-for-coding/k2p6",
    "thinking": { "type": "disabled" },
    "maxTokens": 4096
  }
}
```

### Batch Operations

Your config has automatic batching enabled:
```json
"batch_processing": {
  "enabled": true,
  "batch_size": 5,
  "max_batch_wait_ms": 100
}
```

This groups up to 5 small operations automatically.

### Context Management

Your config truncates at 85% to maintain performance:
```json
"context_management": {
  "max_context_tokens": 200000,
  "truncate_threshold": 0.85
}
```

### Thinking Mode Control

For Kimi agents, you can control reasoning:

```bash
# Enable deep thinking
/acp thinking enabled

# Disable for faster responses
/acp thinking disabled
```

Or configure per-agent in `oh-my-openagent.json`:
```json
"oracle": {
  "model": "kimi-for-coding/k2p6",
  "thinking": { "type": "enabled" }  // or "disabled"
}
```

---

## Example Workflows

### Workflow 1: Adding a Feature

```bash
# 1. Plan (Kimi - ~10s)
@prometheus plan how to add user profiles

# 2. Research (Parallel Kimi instant - ~3s)
@librarian find similar implementations & @explore find user-related code

# 3. Implement (Kimi - ~60s)
@hephaestus implement the user profile feature

# 4. Validate (Parallel Kimi agents - ~8s)
@explore find related tests & @oracle review risk areas & @momus review plan gaps
```

**Total time:** ~80 seconds  
**Total cost:** ~$0.06

### Workflow 2: Bug Investigation

```bash
# Just describe the problem - smart routing handles the rest:
"The app crashes when users click login"

# Sisyphus automatically:
# 1. Routes to @oracle for analysis (deep)
# 2. Spawns @explore to find login code (parallel)
# 3. Delegates focused Kimi category tasks to apply the fix
# 4. Uses Kimi instant/thinking categories to validate
```

### Workflow 3: Code Review

```bash
# Parallel review (4 agents simultaneously)
@explore check for unused imports & @librarian check framework guidance & @oracle review architecture & @momus review plan gaps

# Or simple version:
"Review this PR for issues"
# → Routes to appropriate agents automatically
```

### Workflow 4: Documentation

```bash
# Parallel documentation generation
@explore find public APIs & @librarian find examples & @sisyphus draft documentation
```

---

## Keyboard Shortcuts

### In OpenCode TUI

| Key | Action |
|-----|--------|
| `Tab` | Toggle between input/output panes |
| `Shift+Enter` | Submit prompt |
| `Ctrl+C` | Cancel current request |
| `Esc` | Close UI |
| `↑/↓` | Navigate prompt history |
| `Ctrl+R` | Cycle model variant |
| `~` | Mention file (in input) |
| `@` | Mention agent (in input) |
| `/` | Slash commands |

---

## Tips & Best Practices

### 1. Let Sisyphus Route

Don't overthink model selection. Describe what you want in natural language:

```bash
# Good:
"Find all deprecated functions"
"Design a caching strategy"
"Fix the build error"

# Unnecessary:
"@explore find all deprecated functions"  # Let it route automatically
```

### 2. Use Parallelism

Any independent tasks should run together:

```bash
# Sequential (slow):
@explore find utils
@explore find helpers
@explore find lib

# Parallel (fast):
@explore find utils & @explore find helpers & @explore find lib
```

### 3. Batch Small Tasks

Your config auto-batches, but you can help:

```bash
# Instead of:
"Fix typo A"
"Fix typo B"
"Fix typo C"

# Say:
"Fix typos in these files: A, B, C"
```

### 4. Trust Fallbacks

If a model fails, the agent automatically tries:
1. Primary model
2. Fallback model 1
3. Fallback model 2
4. System default

No action needed from you.

### 5. Monitor Usage

Check your consumption:
```bash
# In OpenCode
/usage

# Or visit:
# https://zen.opencode.ai for Go plan
# https://platform.moonshot.ai for Kimi
```

---

## Summary

**Your setup is optimized for:**
- ✅ Speed through parallelization (12 concurrent agents)
- ✅ Cost control through Kimi instant mode for utility work
- ✅ Deep reasoning through Kimi thinking mode where it matters
- ✅ Zero configuration needed

**Just remember:**
1. Describe what you want naturally
2. Use `@agent` for specific tools
3. Use `&` for parallel work
4. Trust the categories

**Monthly budget:** ~$10-15 for heavy usage

---

## Support & Resources

- **OpenCode Docs:** https://opencode.ai/docs
- **Oh My OpenAgent:** https://github.com/code-yeongyu/oh-my-openagent
- **Kimi Code:** https://www.kimi.com/code

**Configuration Location:**
```
~/.config/opencode/opencode.json
~/.config/opencode/oh-my-openagent.json
```

---

*Happy coding! 🚀*
