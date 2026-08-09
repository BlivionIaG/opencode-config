# OpenCode Setup Manual

**Version:** 1.1  
**Last Updated:** 2026-08-09  
**Subscriptions:** Kimi Code, Alibaba Cloud Model Studio (bailian token plan)

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Your Configuration](#your-configuration)
3. [Agents Guide](#agents-guide)
4. [Categories & Smart Routing](#categories--smart-routing)
5. [Parallel Workflows](#parallel-workflows)
6. [Cost Optimization](#cost-optimization)
7. [MCP Servers](#mcp-servers)
8. [Troubleshooting](#troubleshooting)

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
| `@explore <task>` | Fast search (MiniMax M2.7 HS, ~2s) |
| `@oracle <task>` | Deep analysis (Qwen3.8 Max / Kimi K3-256k fallback, ~8s) |
| `@librarian <task>` | Docs and external reference lookup (MiniMax M2.7 HS, ~3s) |
| `@prometheus <task>` | Implementation planning (Qwen3.8 Max / Kimi K3-256k fallback, ~10s) |
| `agent1 & agent2` | Run agents in parallel |
| `/status` | Check running agents |
| `/models` | Switch models manually |
| `Ctrl+C` | Cancel current task |

### Provider Rate Limits

| Provider | Requests/min | Concurrent |
|----------|--------------|------------|
| Kimi Code | 40 | 4 |
| MiniMax token plan | Account-dependent | Account-dependent |
| Chenco | Account-dependent | Account-dependent |
| Alibaba bailian token plan | Account-dependent | Account-dependent |

---

## Your Configuration

### Enabled Providers

1. **bailian-token-plan-personal** - Alibaba Cloud Model Studio (Singapore token-plan endpoint, Anthropic-compatible). Qwen3.8 Max, Qwen3.7 Max/Plus, Qwen3.6 Flash, GLM-5.2, DeepSeek V4 Pro/Flash. Default primary for deep-reasoning and image-input tasks.
2. **kimi-for-coding** - Kimi K3 and K3-256k (Kimi Code Plan; K3 up to 1M context on Allegro+, K3-256k fixed 256k context). Kept as first fallback for every bailian-anchored slot.
3. **minimax** - MiniMax M3 and M2.7 Highspeed token plan (fast models, up to 1M context)
4. **chenco** - Chenco OpenAI-compatible endpoint (Qwen3.6 model family)

### Model Selection Matrix

| Model | OpenCode ID | Coding (score) | Agentic (score) | Context | Visual | Speed | Efficiency | Best for |
|-------|-------------|----------------|-----------------|---------|--------|-------|------------|----------|
| **Qwen3.8 Max** | `bailian-token-plan-personal/qwen3.8-max` | TBD | TBD | 983K | yes | 3 | 4 | Deep reasoning (256k thinking budget), long-horizon, vision input. Default primary for the K3-slot. |
| **Qwen3.7 Plus** | `bailian-token-plan-personal/qwen3.7-plus` | TBD | TBD | TBD | yes | 4 | 4 | Vision-capable mid-tier; default primary for `multimodal-looker` and `visual-engineering` (Qwen3.8 Max as fallback for harder visual reasoning) |
| **GLM-5.2** | `bailian-token-plan-personal/glm-5.2` | TBD | TBD | TBD | no | 3 | 4 | Deliberative work (refactor, plan review, creative) — different family for diversity |
| **DeepSeek V4 Flash 0731** | `bailian-token-plan-personal/deepseek-v4-flash-0731` | TBD | TBD | TBD | TBD | 5 | 5 | Best intelligence/speed balance for coding; powers `vulcan` (long-horizon autonomous) and `sisyphus-junior` (delegated executor) |
| **Kimi K3** | `kimi-for-coding/k3` | KCB v2 72.9% | Terminal-Bench 2.1 88.3% | 1M | 5 | 2 | 2 | Long-horizon work, video input (now first fallback for Qwen3.8 Max) |
| **Kimi K3-256k** | `kimi-for-coding/k3-256k` | same as K3 | same as K3 | 256K | 3 | 2 | 3 | Visual tasks (image only), architecture, hard debugging, strategic planning; half the quota of K3 |
| **MiniMax M3** | `minimax/MiniMax-M3` | SWE-Bench Pro 59.0% | MCP Atlas 74.2% | 400K | 4 | 4 | 5 | Everyday coding, orchestration, continuation, cost-efficient deep work |
| **MiniMax M2.7 HS** | `minimax/MiniMax-M2.7-highspeed` | SWE-Bench Pro 56.2% | MCP Atlas ~70% | 200K | 2 | 5 | 5 | Search, docs, quick fixes, tests, writing, fast utility work |

*Scores are the best published benchmark available for each model. Coding and agentic benchmarks differ across vendors, so treat them as directional rather than strictly comparable. Visual, speed, and efficiency use 1-5 relative ratings.*

### Published Benchmark Snapshots

| Model | Key benchmark | Score | Notes |
|-------|---------------|-------|-------|
| Kimi K3 | Kimi Code Bench v2 | 72.9% | Moonshot-reported, agentic end-to-end coding |
| Kimi K3 | DeepSWE | 67.5% (KimiCode) / 67.3% (mini-SWE-agent) | Long-horizon real repo issues |
| Kimi K3 | Terminal-Bench 2.1 | 88.3% | CLI/agentic terminal tasks |
| Kimi K3 | FrontierSWE | 81.2% | Frontier implementation/research tasks |
| MiniMax M3 | SWE-Bench Pro | 59.0% | MiniMax-reported real-world SE |
| MiniMax M3 | SWE-Bench Verified | 80.5% | MiniMax-reported |
| MiniMax M3 | Terminal-Bench 2.1 | 66.0% | MiniMax-reported |
| MiniMax M3 | MCP Atlas | 74.2% | MiniMax-reported |
| MiniMax M2.7 | SWE-Bench Pro | 56.2% | From M3 comparison table |
| MiniMax M2.7 | SWE-Bench Verified | 80.2% | From M3 comparison table |

### Model Characteristics

**Kimi K3 (`kimi-for-coding/k3`)**
- ✅ Flagship intelligence; best for long-horizon coding and video input
- ✅ Up to 1M context on Allegro+ plans
- ✅ `reasoning_effort: max` (currently the only supported level; default is `max`)
- ⚠️ Slowest Kimi model; highest Kimi quota use (2× K3-256k)
- ⚠️ Leave sampling settings unset; Kimi rejects non-default `temperature`, `top_p`, `n`, and penalties
- Use for: long-horizon autonomous work, video input (multimodal-looker), deep category tasks

**Kimi K3-256k (`kimi-for-coding/k3-256k`)**
- ✅ Same K3 intelligence, fixed 256K context, half the quota of K3 1M
- ✅ Image input only (no video); `reasoning_effort: max`
- ⚠️ Tasks exceeding 256K context should use K3 1M instead
- Use for: oracle, prometheus, ultrabrain, visual-engineering agents; architecture, hard debugging, strategic planning

**Qwen3.8 Max (`bailian-token-plan-personal/qwen3.8-max`)**
- ✅ Flagship of the bailian token plan; 256K thinking budget, 983K context
- ✅ Image input (text + image)
- ✅ Anthropic-compatible on the Singapore token-plan endpoint
- ⚠️ Long-horizon reasoning burns thinking budget quickly — left at `reasoning: max` for the K3-slot by design
- Use for: deep reasoning, architecture, hard debugging, strategic planning, image input. Default primary for the K3-slot in `omo.jsonc`.

**Qwen3.7 Plus (`bailian-token-plan-personal/qwen3.7-plus`)**
- ✅ Balanced vision-capable model with 8K thinking budget
- ✅ Cheaper than Qwen3.8 Max; good for vision tasks that don't need 256K thinking
- Use for: default primary for `multimodal-looker` and `visual-engineering` (Qwen3.8 Max as fallback for harder visual reasoning)

**GLM-5.2 (`bailian-token-plan-personal/glm-5.2`)**
- ✅ Deliberative reasoning model with 8K thinking budget
- ✅ Different model family from Qwen/DeepSeek — useful for diversity
- Use for: deliberative work (refactor, plan review, creative). Default primary for the deliberative slot in `omo.jsonc`.

**DeepSeek V4 Flash 0731 (`bailian-token-plan-personal/deepseek-v4-flash-0731`)**
- ✅ Best intelligence/speed balance for coding among the bailian lineup
- ✅ Token-plan cost (per the user's evaluation: better than DeepSeek V4 Pro for agentic use)
- ✅ Now powers `vulcan` (long-horizon autonomous) and `sisyphus-junior` (delegated executor)
- ⚠️ Provider config has no reasoning/thinking options — agent-level `reasoning: "auto"` is what enables reasoning
- Use for: agentic workhorse, delegated task execution, long-horizon autonomous work where v4-flash's speed advantage matters

**MiniMax M3 (`minimax/MiniMax-M3`)**
- ✅ Best speed/intelligence balance in the MiniMax family
- ✅ 400K context, multimodal (text/image/video input), tool-call capable
- ✅ Cheap MiniMax quota use
- Use for: orchestration, continuation, everyday coding, cost-efficient deep work

**MiniMax M2.7 Highspeed (`minimax/MiniMax-M2.7-highspeed`)**
- ✅ Fastest, cheapest model in the stack
- ✅ 200K context, 131K output, tool-call capable
- ✅ Configured as OpenCode `small_model`
- ⚠️ Lower reasoning ceiling than M3 or Kimi
- Use for: search, docs, quick fixes, tests, writing, simple responses

**Chenco Qwen3.6 Models**
- ✅ OpenAI-compatible LiteLLM endpoint
- ✅ API key loaded from `CHENCO_API_KEY`
- ✅ Available models: `chenco/qwen3.6-instruct`, `chenco/qwen3.6-coding`, `chenco/qwen3.6-agent`, `chenco/qwen3.6-vision`
- ⚠️ Limits and model capabilities depend on the Chenco gateway configuration
- Use for: manually selected Chenco-backed Qwen3.6 model runs

### Thinking & Variant Configuration

| Model | OpenCode setting | Why |
|-------|------------------|-----|
| **Kimi K3 / K3-256k** | `"variant": "max"` | K3 uses the top-level `reasoning_effort` field; at launch only `max` is supported and it is the default. Setting `variant: max` makes the intent explicit. |
| **Qwen3.8 Max** | `"reasoning": "max"` (agent) + provider-level `thinking: { budgetTokens: 262144 }` | qwen3.8-max uses both top-level `reasoning` and provider-level thinking budget. The 256K budget is set in `opencode.json`; the agent `reasoning: max` enables max reasoning on top. |
| **Qwen3.7 Plus / GLM-5.2** | `"thinking": { "type": "enabled" }` (agent) | Each bailian model has its own `thinking: { budgetTokens: 8192 }` set in the provider config. The agent-level `thinking.enabled` opt-in is kept for documentation. |
| **DeepSeek V4 Flash 0731** | `"reasoning": "auto"` (agent) | Provider has no reasoning config. The agent's `reasoning: auto` is what enables reasoning. No budget controls exposed. |
| **MiniMax M3** | `"thinking": { "type": "adaptive" }` (or `disabled`) | M3 uses `adaptive` to enable thinking; it does **not** support `budgetTokens`. `disabled` skips thinking for faster responses. |
| **MiniMax M2.7 Highspeed** | `"thinking": { "type": "disabled" }` (accepted but ignored) | M2.7 models always reason; passing `disabled` is accepted but thinking remains on. Kept here to document intent. |

**Runtime control:**
- Use `/acp thinking enabled` or `/acp thinking disabled` to toggle thinking in the current session.
- Use `/variants` (or `Ctrl+T`) to cycle model variants such as `max`, `high`, `low`, or `none`.
- For K3, only `max` reasoning effort is currently available; lower levels will arrive in later updates.

### Model Usage & Routing

| Model | Where it is used | Why it was chosen |
|-------|------------------|-------------------|
| **Qwen3.8 Max** | Agents: `hephaestus`, `oracle`, `prometheus`<br>Categories: `deep`, `ultrabrain` | Primary for the K3-slot. 256K thinking budget + 983K context + image input. Kimi K3-256k kept as first fallback. Used for vision only as a fallback (Qwen3.7 Plus is the primary for vision tasks). |
| **Qwen3.7 Plus** | Agents: `multimodal-looker`<br>Categories: `visual-engineering` | Primary for vision tasks. 8K thinking budget + vision input. Cheaper than Qwen3.8 Max for typical vision work; Qwen3.8 Max as fallback for harder visual reasoning. |
| **GLM-5.2** | Agents: `metis`, `momus`<br>Categories: `refactor`, `artistry`, `unspecified-high` | Primary for the deliberative/refactor/creative slot. Deliberative reasoning with 8K thinking budget; different model family for diversity. Kimi K3-256k kept as first fallback. |
| **DeepSeek V4 Flash 0731** | Agents: `vulcan` (`opencode.json`), `sisyphus-junior` | Agentic workhorse with best intelligence/speed balance per the user's evaluation. Powers `vulcan` (long-horizon autonomous) and `sisyphus-junior` (delegated executor). No reasoning/thinking config at provider level — agent-level `reasoning: "auto"` is mandatory. |
| **Kimi K3-256k** | First fallback for `oracle`, `prometheus`, `ultrabrain`, `visual-engineering`, `metis`, `momus`, `refactor`, `artistry`, `unspecified-high`<br>Also fallback for `hephaestus`, `multimodal-looker`, `deep` (behind K3 1M) | Same K3 intelligence at fixed 256K context; half the quota of K3 1M. Best for architecture, hard debugging, strategic planning, image-based visual tasks. |
| **Kimi K3** | First fallback for `hephaestus`, `multimodal-looker`, `deep` | Highest intelligence in the stack; native visual and video understanding; best for long-horizon coding, video input. Up to 1M context on Allegro+ plans. |
| **MiniMax M3** | Agents: `sisyphus`, `atlas` | Best speed/intelligence/cost balance for orchestration, continuation, and everyday coding. Keeps the main loop and long-running handlers fast and cheap. |
| **MiniMax M2.7 Highspeed** | Agents: `librarian`, `explore`<br>Categories: `quick`, `fix`, `search`, `test`, `explain`, `writing`, `unspecified-low` | Fastest, cheapest model for high-volume utility work: search, docs, quick fixes, tests, and writing. Configured as the OpenCode `small_model`. |

**Fallback logic:** Bailian Qwen3.8 Max primary falls back to Kimi K3-256k → MiniMax M3. Bailian Qwen3.7 Plus primary falls back to Qwen3.8 Max (vision) → Kimi K3 → MiniMax M3. Bailian GLM-5.2 primary falls back to Kimi K3-256k → MiniMax M3. Bailian DeepSeek V4 Flash primary falls back to MiniMax M3 → MiniMax M2.7 HS. MiniMax M3 primary falls back to K3-256k. MiniMax M2.7 highspeed primary falls back to M3. This keeps the most capable Kimi models behind the cheaper bailian options for cost control (with bailian primary), while ensuring a reasoning model is always available if a provider fails.

## Agents Guide

### Primary Agents

| Agent | Model | Mode / Variant | Max Tokens | Use For |
|-------|-------|----------------|------------|---------|
| **Sisyphus** | `minimax/MiniMax-M3` | thinking adaptive | 16384 | Main orchestrator, delegates tasks (K3-256k fallback) |
| **Atlas** | `minimax/MiniMax-M3` | thinking disabled / instant | 16384 | Plan orchestration, task coordination, continuation |
| **Hephaestus** | `bailian-token-plan-personal/qwen3.8-max` | `reasoning: max` | 32768 | Deep autonomous work, long-horizon implementation. Kimi K3 first fallback. |
| **Vulcan** | `bailian-token-plan-personal/deepseek-v4-flash-0731` | native agent (`agents/vulcan.md`) | 32768 | Deep autonomous work, long-horizon implementation. v4-flash tuned for fast intelligent agentic execution. |
| **Prometheus** | `bailian-token-plan-personal/qwen3.8-max` | `reasoning: max` | 32768 | Strategic planning. Kimi K3-256k first fallback. |

### Utility Agents

| Agent | Model | Mode / Variant | Max Tokens | Use For |
|-------|-------|----------------|------------|---------|
| **Explore** | `minimax/MiniMax-M2.7-highspeed` | thinking disabled | 8192 | Fast codebase grep, search |
| **Librarian** | `minimax/MiniMax-M2.7-highspeed` | thinking disabled | 16384 | Documentation and external reference search |
| **Multimodal-Looker** | `bailian-token-plan-personal/qwen3.7-plus` | `reasoning: max` | 32768 | Vision tasks, screenshots, UI analysis. Qwen3.8 Max first fallback for harder visual reasoning. |
| **Sisyphus-Junior** | `bailian-token-plan-personal/deepseek-v4-flash-0731` | `reasoning: auto` | 4096-32768 | Focused delegated task execution. v4-flash as agentic workhorse; MiniMax M3 fallback. |

### Special Agents

| Agent | Model | Mode / Variant | Max Tokens | Use For |
|-------|-------|----------------|------------|---------|
| **Oracle** | `bailian-token-plan-personal/qwen3.8-max` | `reasoning: max` | 32768 | Architecture analysis, debugging. Kimi K3-256k first fallback. |
| **Metis** | `bailian-token-plan-personal/glm-5.2` | thinking enabled | 32768 | Plan consulting. Kimi K3-256k first fallback. |
| **Momus** | `bailian-token-plan-personal/glm-5.2` | thinking enabled | 32768 | Plan review. Kimi K3-256k first fallback. |

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
| **quick** | fix, typo, rename, add import | MiniMax M2.7 HS, 4096 maxTokens | ~1-2s |
| **search** | find, search, grep, locate | MiniMax M2.7 HS, 4096 maxTokens | ~1-2s |
| **explain** | explain, what does, how to | MiniMax M2.7 HS, 8192 maxTokens | ~2-3s |
| **test** | test, spec, validate | MiniMax M2.7 HS, 8192 maxTokens | ~3-4s |
| **writing** | write, document, describe | MiniMax M2.7 HS, 8192 maxTokens | ~2-3s |
| **fix** | fix, correct, repair | MiniMax M2.7 HS, 4096 maxTokens | ~1-2s |
| **refactor** | refactor, cleanup, optimize | GLM-5.2 thinking, 32768 maxTokens | ~8s (K3-256k fallback) |
| **deep** | debug, investigate, analyze | Qwen3.8 Max reasoning, 32768 maxTokens | ~8s (Kimi K3 fallback) |
| **ultrabrain** | architect, design, plan | Qwen3.8 Max reasoning, 32768 maxTokens | ~10s (Kimi K3-256k fallback) |
| **visual-engineering** | UI, frontend, screenshot, design | Qwen3.7 Plus reasoning, 32768 maxTokens | ~8s (Qwen3.8 Max / Kimi K3-256k fallback) |
| **artistry** | creative, unconventional, novel | GLM-5.2 thinking, 32768 maxTokens | ~8s (K3-256k fallback) |
| **unspecified-low** | lightweight, simple, small | MiniMax M2.7 HS, 4096 maxTokens | ~1-2s |
| **unspecified-high** | complex, important, high stakes | GLM-5.2 reasoning, 32768 maxTokens | ~8s (K3-256k fallback) |

### Examples

**Automatic instant routing (fast MiniMax, thinking disabled):**
```bash
"Find all console.log statements"           → @explore
"Add import for lodash"                      → @sisyphus-junior
"Fix typo in variable name"                  → quick/fix category
"Explain what this regex does"               → explain category
"Run tests for auth module"                  → test category
```

**Automatic quality routing (Bailian for strategic planning, hard debugging, and visual work; Kimi as first fallback):**
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

Your config uses bailian (Qwen3.8 Max / GLM-5.2) for quality-critical reasoning, Kimi as first fallback, and MiniMax token-plan routing for fast utility work, with explicit instant/thinking settings per agent and category.

**Check status:**
```bash
/status
```

**Max parallel per provider:**
- Kimi: up to 4 agents simultaneously
- MiniMax token plan: account-dependent
- Alibaba bailian token plan: account-dependent

---

## Cost Optimization

### Cost Breakdown

| Operation | Model | Cost | Time |
|-----------|-------|------|------|
| Simple search | MiniMax M2.7 HS | Lower Kimi/bailian quota use | ~1-2s |
| Quick fix | MiniMax M2.7 HS | Lower Kimi/bailian quota use | ~1-2s |
| Code explanation | MiniMax M2.7 HS | Lower Kimi/bailian quota use | ~2-3s |
| Test generation | MiniMax M2.7 HS | Lower Kimi/bailian quota use | ~3-4s |
| Refactoring | GLM-5.2 (K3-256k fallback) | Token-plan cost | ~8s |
| Deep analysis | Qwen3.8 Max (K3-256k fallback) | Token-plan cost | ~8s |
| Architecture planning | Qwen3.8 Max (K3-256k / MiniMax M3 fallback) | Token-plan cost | ~8-10s |

### Your Monthly Budget

**Kimi Code Subscription:**
- ~9,250 Kimi requests (typical usage, only consumed when bailian is rate-limited)
- Rate limit: 40 req/min

**Alibaba Cloud Model Studio (bailian token plan):**
- Token-plan model — consumed by Qwen3.8 Max, Qwen3.7 Plus, GLM-5.2, and DeepSeek V4 Flash
- Default primary for deep reasoning, vision, deliberative, and agentic work

**Typical Monthly Usage:**
- MiniMax M2.7 highspeed for search, quick fixes, explanations, tests, writing, and fast utility work
- MiniMax M3 for orchestration (Sisyphus), continuation (Atlas), and cost-efficient everyday coding
- Qwen3.8 Max for strategic planning, architecture, hard debugging, and long-horizon investigation (Kimi K3-256k first fallback)
- Qwen3.7 Plus for vision tasks (multimodal-looker, visual-engineering) — Qwen3.8 Max fallback for harder visual work
- GLM-5.2 for refactoring, plan consulting, plan review, critique, and creative tasks (Kimi K3-256k first fallback)
- DeepSeek V4 Flash 0731 for `@vulcan` long-horizon autonomous work and `sisyphus-junior` delegated task execution
- Runtime fallback retries quota, timeout, and provider errors, and escalates stalled primary requests after 30 seconds

### Cost-Saving Tips

✅ **DO:**
- Use simple language for simple tasks ("find X" → MiniMax M2.7 HS)
- Run independent tasks in parallel with `&`
- Trust automatic routing (it's optimized)
- Use `@explore` and `@librarian` for utility work
- Batch small operations (automatic batching enabled)

❌ **DON'T:**
- Use `@oracle` for "find this file" (wastes bailian/Kimi quota)
- Run everything sequentially (parallel is 3-4x faster)
- Force thinking mode for trivial tasks
- Request long outputs when short ones suffice

---

## MCP Servers

External tools exposed via the [Model Context Protocol](https://modelcontextprotocol.io). Each MCP server adds to the context budget, so enable sparingly.

### n8n-mcp (czlonkowski/n8n-mcp)

Gives agents full knowledge of the 1,851 n8n nodes + read/write access to your n8n instance workflows, executions, and credentials.

**Configuration** (`opencode.json` → `mcp.n8n-mcp`):

| Field | Value | Notes |
|---|---|---|
| `type` | `local` | stdio transport |
| `command` | `["npx", "-y", "n8n-mcp"]` | First run downloads the package |
| `enabled` | `false` (toggle to `true` to use) | Disabled by default to keep context lean |
| `timeout` | `30000` (ms) | Cold start loads a ~540MB node DB |
| `N8N_API_URL` | `{env:N8N_API_URL}` | e.g. `https://n8n.chenco.dev` |
| `N8N_API_KEY` | `{env:N8N_API_KEY}` | From n8n → Settings → API |
| `NODE_DB_PATH` | `~/.config/opencode/data/n8n-nodes.db` | Cached node documentation DB (gitignored) |

**Setup:**

1. Add to your shell config (`~/.zshenv`, `~/.bashrc`, etc.):
   ```bash
   export N8N_API_URL="https://your-n8n-instance.example.com"
   export N8N_API_KEY="your_n8n_api_key"
   ```
2. In `opencode.json`, flip `"enabled": false` → `"true"` under `mcp.n8n-mcp`.
3. In a prompt, explicitly opt in: *"use n8n-mcp to list my failing workflows"*.

**Tools exposed (~20):**

- **Core / docs (7):** `tools_documentation`, `search_nodes`, `get_node`, `validate_node`, `validate_workflow`, `search_templates`, `get_template`
- **Workflow mgmt (10):** `n8n_create_workflow`, `n8n_get_workflow`, `n8n_list_workflows`, `n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_workflow_versions`, `n8n_deploy_template`
- **Execution (2):** `n8n_test_workflow`, `n8n_executions`
- **Credentials / system (4):** `n8n_manage_credentials`, `n8n_audit_instance`, `n8n_health_check`, plus diagnostic helpers

All prefixed with `n8n-mcp_` in tool listings (e.g. `n8n-mcp_n8n_list_workflows`).

**Safety notes** (from upstream README):

- Never edit production workflows directly — duplicate, edit, validate, then promote.
- AI-generated configs can be unpredictable; always validate with `n8n_validate_workflow` after deploy.
- The `N8N_API_KEY` is a powerful credential (full workflow R/W, credentials R/W, executions R/W). Rotate if exposed.

**Disabling per-agent:**

To keep it off globally but enable for a specific agent, add to `omo.jsonc`:

```jsonc
"tools": {
  "n8n-mcp_*": false
}
```

Then opt in per agent via the agent's `tools` block.

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

# Edit omo.jsonc (repo copy of ~/.omo/omo.jsonc):
"agents": {
  "defaults": {
    "maxConcurrent": 8  # Reduced from 12
  }
}
```

**Issue: Task fails**
```bash
# Confirm the resolved Kimi for Coding config:
opencode debug config

# Check available Kimi models:
opencode models kimi-for-coding

# Check MiniMax fast model metadata:
opencode models minimax --verbose

# Check Bailian (Alibaba) model metadata:
opencode models bailian-token-plan-personal --verbose
```

**Issue: Wrong model selected**
```bash
# Override manually:
/models
# Select: kimi-for-coding/k3

# Fast/small model is configured as:
# minimax/MiniMax-M2.7-highspeed

# Default primary for deep reasoning is:
# bailian-token-plan-personal/qwen3.8-max

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
| `opencode.json` | `~/.config/opencode/` | Provider settings, session defaults, native agents (vulcan) |
| `omo.jsonc` | repo: `~/.config/opencode/omo.jsonc` → live: `~/.omo/omo.jsonc` | Agent & category config (unified OMO schema) |
| `scripts/sync-omo.sh` | `~/.config/opencode/scripts/` | push/pull/check/doctor sync between repo and live config |
| `agents/vulcan.md` | `~/.config/opencode/` | Vulcan deep-worker system prompt |

**Since oh-my-openagent 4.19.x:** the plugin config moved from
`~/.config/opencode/oh-my-openagent.jsonc` to `~/.omo/omo.jsonc` (automatic
migration on first launch; backups under `~/.omo/migration-backup-*`). This
repo version-controls the canonical copy and syncs it — no symlink, because
the plugin can rewrite the live path and a symlink breaks silently:

```bash
scripts/sync-omo.sh push    # repo -> ~/.omo/omo.jsonc (after editing the repo copy)
scripts/sync-omo.sh pull    # live -> repo (after a plugin migration/upgrade writes it)
scripts/sync-omo.sh check   # detect drift between the two
scripts/sync-omo.sh doctor  # JSONC validation + plugin doctor + agent roster
```

Schema notes for the unified format: the whole config is wrapped in an
`"[opencode]"` scope block. **Agents** use `model` + `fallback_models` (with
`reasoning`/`variant`/`thinking`/`mode`/`displayName` as sibling keys).
**Categories** use `models[]` arrays (first entry = primary, rest =
fallbacks; entries can be `{model, reasoning}` objects or plain strings).
Note: the 4.19.4 auto-migration emitted `models[]` for *agents* too, which
the schema rejects ("Unknown field" warnings) — if you see those, convert
agent entries to `model` + `fallback_models` as in this repo's `omo.jsonc`.

**Do NOT** recreate `oh-my-openagent.json[c]` in `~/.config/opencode/` — the
plugin will detect it and re-run the migration.

**Known 4.19.4 quirk — keep `fallback_models` for agents:** `oh-my-openagent
doctor` warns "Deprecated reasoning config key: replace fallback_models with
models". Do NOT act on it for agent entries. The TUI sidebar's config banner
is driven by a different validator that rejects `models[]` on agents
("Unknown config key") — the two checks contradict each other in 4.19.4.
`fallback_models` keeps the TUI banner green; the doctor deprecations are
cosmetic. Revisit when upstream reconciles the two (check after plugin
upgrades with `scripts/sync-omo.sh doctor`).

**tui.json is managed by opencode itself** — it rewrites the file to mirror
opencode.json's plugin array on startup. Don't hand-edit it; commit whatever
opencode writes.

### Reset Everything

```bash
# Reinstall the live config from the repo:
scripts/sync-omo.sh push

# Or restore from a migration backup:
cp ~/.omo/migration-backup-*/.config/opencode/oh-my-openagent.jsonc /tmp/legacy.jsonc
```

---

## Advanced Usage

### Custom Categories

Add to `omo.jsonc`:
```json
"categories": {
  "my-custom-category": {
    "models": [
      { "model": "kimi-for-coding/k3", "reasoning": "max" },
      "minimax/MiniMax-M3"
    ]
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

Or configure per-agent in `omo.jsonc`:
```json
"oracle": {
  "model": "kimi-for-coding/k3-256k",
  "reasoning": "max",
  "fallback_models": ["minimax/MiniMax-M3"]
}
```

---

## Example Workflows

### Workflow 1: Adding a Feature

```bash
# 1. Plan (Kimi K3-256k - ~10s)
@prometheus plan how to add user profiles

# 2. Research (Parallel MiniMax M2.7 HS - ~3s)
@librarian find similar implementations & @explore find user-related code

# 3. Implement (Kimi K3 1M - ~60s)
@vulcan implement the user profile feature

# 4. Validate (Parallel agents - ~8s)
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
# 4. Uses fast MiniMax categories to validate and Kimi reasoning categories to deep-check
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
- ✅ Speed through parallel agent execution
- ✅ Cost control through MiniMax M2.7 highspeed for utility work
- ✅ Deep reasoning through Bailian (Qwen3.8 Max / GLM-5.2) where it matters, with Kimi as first fallback
- ✅ Zero configuration needed

**Just remember:**
1. Describe what you want naturally
2. Use `@agent` for specific tools
3. Use `&` for parallel work
4. Trust the categories

**Monthly budget:** You have a Kimi Code Allegro €100 plan, Alibaba Cloud Model Studio (bailian token plan), and a MiniMax token plan €50; actual spend depends on usage mix.

---

## Support & Resources

- **OpenCode Docs:** https://opencode.ai/docs
- **Oh My OpenAgent:** https://github.com/code-yeongyu/oh-my-openagent
- **Kimi Code:** https://www.kimi.com/code

**Configuration Location:**
```
~/.config/opencode/opencode.json       (providers, defaults, native agents)
~/.omo/omo.jsonc                       (live agent config; synced from repo via scripts/sync-omo.sh)
~/.config/opencode/omo.jsonc           (canonical copy, version-controlled)
```

---

*Happy coding! 🚀*
