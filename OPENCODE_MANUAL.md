# OpenCode Setup Manual

**Version:** 1.0  
**Last Updated:** 2026-04-01  
**Subscriptions:** Kimi Code + OpenCode Go

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
| `@explore <task>` | Fast search (MiniMax, ~1s) |
| `@oracle <task>` | Deep analysis (Kimi thinking, ~8s) |
| `@fixer <task>` | Quick fixes (MiniMax, ~1s) |
| `@test-engineer <task>` | Write tests (MiniMax, ~3s) |
| `agent1 & agent2` | Run agents in parallel |
| `/status` | Check running agents |
| `/models` | Switch models manually |
| `Ctrl+C` | Cancel current task |

### Provider Rate Limits

| Provider | Requests/min | Concurrent |
|----------|--------------|------------|
| OpenCode Go (MiniMax) | 100 | 10 |
| Kimi Code | 40 | 4 |

---

## Your Configuration

### Enabled Providers

1. **kimi-for-coding** - Kimi K2.6 (powerful reasoning, 256K context)
2. **opencode-go** - MiniMax M2.5 (fast & cheap, 100K requests/month)

### Model Characteristics

**Kimi K2.6 (kimi-for-coding/k2p6)**
- ✅ Deep reasoning, architecture, debugging
- ✅ Multimodal (vision + text)
- ✅ 256K context window
- ✅ Thinking and instant modes via `thinking.type`
- ⚠️ Slower, more expensive
- ⚠️ Leave sampling settings unset; K2.6 rejects non-default `temperature`, `top_p`, `n`, and penalties
- Use for: complex planning, debugging, visual tasks

**MiniMax M2.5 (opencode-go/minimax-m2.5)**
- ✅ Very fast (100 tokens/s)
- ✅ Very cheap (8x cheaper than Kimi)
- ✅ 100K requests/month on Go plan
- ⚠️ Less reasoning depth
- Use for: search, grep, simple fixes, tests

---

## Agents Guide

### Primary Agents

| Agent | Model | Use For | Fallback |
|-------|-------|---------|----------|
| **Sisyphus** | Kimi (instant) | Main orchestrator, delegates tasks | MiniMax |
| **Oracle** | Kimi (thinking) | Architecture analysis, debugging | GLM-5 |
| **Hephaestus** | Kimi (thinking) | Deep autonomous work, research | GLM-5 |
| **Prometheus** | Kimi (thinking) | Strategic planning | GLM-5 |
| **Metis** | Kimi (thinking) | Plan consulting | GLM-5 |
| **Momus** | Kimi (thinking) | Plan review | GLM-5 |

### Utility Agents

| Agent | Model | Use For | Fallback |
|-------|-------|---------|----------|
| **Explore** | MiniMax | Fast codebase grep, search | MiniMax M2.7 |
| **Librarian** | MiniMax | Documentation search | GLM-5 |
| **Librarian-Junior** | MiniMax | Parallel doc search | MiniMax M2.7 |
| **Sisyphus-Junior** | MiniMax | Quick task execution | MiniMax M2.7 |
| **Atlas-Junior** | MiniMax | Parallel execution | MiniMax M2.7 |
| **Code-Runner** | MiniMax | Syntax validation | GLM-5 |
| **Test-Engineer** | MiniMax | Write & run tests | MiniMax M2.7 |
| **Fixer** | MiniMax | Quick fixes, typos | MiniMax M2.7 |
| **Explainer** | MiniMax | Code explanation | GLM-5 |

### Special Agents

| Agent | Model | Use For |
|-------|-------|---------|
| **Atlas** | Kimi (instant) | Plan orchestration, task coordination |
| **Multimodal-Looker** | Kimi (instant) | Vision tasks, screenshots, UI analysis |

### How to Use Agents

**Direct delegation:**
```bash
@explore find all TODO comments
@oracle analyze why tests are failing
@fixer fix the typo in README.md
```

**Parallel execution:**
```bash
# Run multiple agents simultaneously
@explore find auth files & @librarian search auth docs & @test-engineer write auth tests

# This completes in ~2 seconds instead of ~6 seconds
```

---

## Categories & Smart Routing

### Automatic Category Detection

Sisyphus automatically categorizes your requests based on keywords:

| Category | Trigger Keywords | Model | Speed |
|----------|-----------------|-------|-------|
| **quick** | fix, typo, rename, add import | MiniMax | ~1s |
| **search** | find, search, grep, locate | MiniMax | ~1s |
| **explain** | explain, what does, how to | MiniMax | ~2s |
| **test** | test, spec, validate | MiniMax | ~3s |
| **refactor** | refactor, cleanup, optimize | MiniMax | ~4s |
| **deep** | debug, investigate, analyze | Kimi thinking | ~8s |
| **ultrabrain** | architect, design, plan | Kimi thinking | ~10s |
| **visual-engineering** | UI, frontend, screenshot, design | Kimi thinking | ~8s |
| **writing** | write, document, describe | MiniMax | ~2s |
| **fix** | fix, correct, repair | MiniMax | ~1s |

### Examples

**Automatic MiniMax routing (fast & cheap):**
```bash
"Find all console.log statements"           → @explore
"Add import for lodash"                      → @sisyphus-junior
"Fix typo in variable name"                  → @fixer
"Explain what this regex does"               → @explainer
"Run tests for auth module"                  → @test-engineer
"Refactor this function"                     → @code-runner
```

**Automatic Kimi routing (deep reasoning):**
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
@explore find utils & @librarian search docs & @test-engineer validate

# Time: ~2 seconds total (vs ~6 seconds sequential)
```

### Common Parallel Patterns

**Pattern 1: Multi-file Search**
```bash
@explore find auth code & @explore find user code & @explore find session code
```

**Pattern 2: Code Review**
```bash
@code-runner check syntax & @test-engineer validate tests & @fixer check for issues & @explainer review logic
```

**Pattern 3: Research & Planning**
```bash
@librarian find examples & @explore find similar implementations & @oracle analyze approach
```

**Pattern 4: Testing**
```bash
@test-engineer write unit tests & @test-engineer write integration tests & @code-runner check coverage
```

### Background Agents

Your config supports **12 concurrent background agents**:
- 10 from OpenCode Go (MiniMax)
- 4 from Kimi Code

**Check status:**
```bash
/status
```

**Max parallel per provider:**
- MiniMax: up to 10 agents simultaneously
- Kimi: up to 4 agents simultaneously

---

## Cost Optimization

### Cost Breakdown

| Operation | Model | Cost | Time |
|-----------|-------|------|------|
| Simple search | MiniMax | ~$0.0001 | ~1s |
| Quick fix | MiniMax | ~$0.0001 | ~1s |
| Code explanation | MiniMax | ~$0.0002 | ~2s |
| Test generation | MiniMax | ~$0.0003 | ~3s |
| Refactoring | MiniMax | ~$0.0005 | ~4s |
| Deep analysis | Kimi | ~$0.005 | ~8s |
| Architecture planning | Kimi | ~$0.006 | ~10s |

### Your Monthly Budget

**OpenCode Go ($10/month):**
- 100,000 MiniMax requests
- Rate limit: 100 req/min

**Kimi Code Subscription:**
- ~9,250 Kimi requests (typical usage)
- Rate limit: 40 req/min

**Typical Monthly Usage:**
- 70% MiniMax (70,000 requests) = ~$3-4
- 25% Kimi (2,300 requests) = ~$5-8
- 5% GLM-5 fallback = ~$1
- **Total: ~$10-15/month**

### Cost-Saving Tips

✅ **DO:**
- Use simple language for simple tasks ("find X" → MiniMax)
- Run independent tasks in parallel with `&`
- Trust automatic routing (it's optimized)
- Use `@explore`, `@librarian`, `@fixer` for utility work
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
# Check fallback chain in config
# Agent automatically tries fallback models:
# MiniMax → MiniMax M2.7 → GLM-5 (for utility agents)
# Kimi → GLM-5 (for reasoning agents)

# Check with:
bunx oh-my-opencode doctor
```

**Issue: Wrong model selected**
```bash
# Override manually:
/models
# Select: kimi-for-coding/k2p6 or opencode-go/minimax-m2.5

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
    "model": "opencode-go/minimax-m2.5",
    "maxTokens": 2048
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

# 2. Research (Parallel MiniMax - ~2s)
@librarian find similar implementations & @explore find user-related code

# 3. Implement (Kimi - ~60s)
@hephaestus implement the user profile feature

# 4. Validate (Parallel MiniMax - ~5s)
@test-engineer write tests & @code-runner check syntax & @fixer review
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
# 3. Delegates @fixer to apply fix (parallel)
# 4. Calls @test-engineer to validate (parallel)
```

### Workflow 3: Code Review

```bash
# Parallel review (4 agents simultaneously)
@explore check for unused imports & @test-engineer validate edge cases & @oracle review architecture & @code-runner check for errors

# Or simple version:
"Review this PR for issues"
# → Routes to appropriate agents automatically
```

### Workflow 4: Documentation

```bash
# Parallel documentation generation
@explore find public APIs & @explainer document functions & @librarian find examples & @code-runner generate code snippets
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
- ✅ Cost through smart routing (70% MiniMax, 30% Kimi)
- ✅ Reliability through fallback chains
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
- **OpenCode Go:** https://opencode.ai/go
- **Kimi Code:** https://www.kimi.com/code

**Configuration Location:**
```
~/.config/opencode/opencode.json
~/.config/opencode/oh-my-openagent.json
```

---

*Happy coding! 🚀*
