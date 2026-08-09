# Agent Rules for OpenCode Configuration Repository

This document defines mandatory rules for AI agents working with this repository.

## Security Rules (CRITICAL)

### Rule 1: No Credentials in Git
**NEVER commit API keys, tokens, passwords, or secrets to this repository.**

**Prohibited patterns:**
- Files matching: `*secret*`, `*credential*`, `*api_key*`, `*token*`, `*password*`
- Extensions: `*.pem`, `*.key`, `*.p12`
- Environment files: `.env`, `.env.local`, `.env.*`

**Where credentials belong:**
In your shell config — keys live outside the repo entirely, loaded by every shell invocation:

```bash
# zsh: ~/.zshenv (loaded for every zsh, including non-interactive scripts)
export KIMI_API_KEY="your_key"
export MINIMAX_API_KEY="your_key"

# bash: ~/.bashrc (interactive) or ~/.bash_profile (login shells)
# fish: ~/.config/fish/config.fish (use `set -x KEY value`)
```

`opencode.json` references these via `{env:VAR_NAME}` placeholders, so the provider config stays secret-free.

**Verification before commit:**
```bash
# Check for secrets in staged files
git diff --cached | grep -i "api_key\|secret\|token\|password"

# Or use git-secrets if available
git secrets --scan
```

### Rule 2: Validate Security Before Push
Always run these checks before pushing:

```bash
# Check what will be pushed
git diff --stat origin/master

# Review all changes
git diff origin/master

# Defense-in-depth: ensure no .env or secret-shaped files slipped into staging
git diff --cached --name-only | grep -E "\.env|secret|credential" && echo "BLOCKED: Secrets detected" || echo "OK"
```

## Commit Rules

### Rule 3: Descriptive Commits Required
Every commit must clearly describe what was changed and why.

**Format:**
```
<type>: <short description>

<detailed explanation>

- What changed: <specific changes>
- Why: <reasoning>
- Testing: <how verified>
```

**Types:**
- `feat`: New agent, configuration, or feature
- `fix`: Bug fix or correction
- `update`: Modification to existing config
- `docs`: Documentation changes
- `security`: Security-related changes
- `refactor`: Restructuring without functional change

**Examples:**

✅ **Good:**
```
feat: Add @test-engineer agent for automated testing

Added new test-engineer agent configuration to omo.jsonc.
This agent specializes in writing and running test suites.

- What changed: Added agent definition with MiniMax model
- Why: Need dedicated agent for test generation
- Testing: Verified agent loads correctly with `opencode doctor`
```

✅ **Good:**
```
update: Increase context window for oracle agent

Bumped maxTokens from 8192 to 16384 for oracle agent to handle
larger codebases during architecture analysis.

- What changed: oracle.maxTokens in omo.jsonc
- Why: Architecture analysis was failing on large projects
- Testing: Tested with 500-file codebase, analysis completed
```

❌ **Bad:**
```
update stuff
```

❌ **Bad:**
```
fix
```

### Rule 4: Atomic Commits
Each commit should represent a single logical change:

- ✅ One agent addition = one commit
- ✅ One bug fix = one commit  
- ✅ One config update = one commit
- ❌ Multiple unrelated changes in one commit

## Workflow Rules

### Rule 5: Commit and Push Working Changes
**When you make a modification that works, you must commit and push it.**

**Procedure:**

1. **Test your changes:**
   ```bash
   # Verify syntax
   grep -v "^\s*//" omo.jsonc | python3 -c "import json,sys,re; json.loads(re.sub(r',(\s*[}]])', r'\1', sys.stdin.read()))" > /dev/null
   
   # Test configuration loads
   opencode doctor
   ```

2. **Stage changes:**
   ```bash
   git add <files>
   ```

3. **Write descriptive commit:**
   ```bash
   git commit -m "type: description

   Detailed explanation of what changed and why."
   ```

4. **Push to remote:**
   ```bash
   git push origin master
   ```

**Never leave uncommitted working changes.**

### Rule 6: Pull Before Modifying
Always sync with remote before making changes:

```bash
git pull origin master
```

This prevents merge conflicts.

### Rule 7: No Force Pushes
**Never use `git push --force` on this repository.**

If you need to fix history, use `git revert` or create a new commit.

## Configuration Rules

### Rule 8: Validate JSON Syntax
All JSON files must be valid:

```bash
# Validate before committing
grep -v "^\s*//" omo.jsonc | python3 -c "import json,sys,re; json.loads(re.sub(r',(\s*[}]])', r'\1', sys.stdin.read()))" > /dev/null && echo "Valid JSONC" || echo "Invalid JSONC"
python3 -m json.tool opencode.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

### Rule 9: Follow Existing Patterns
When adding new configurations, match the existing style:

- Use same indentation (2 spaces)
- Follow naming conventions (kebab-case for agents)
- Include fallback_models where appropriate
- Use descriptive comments

**Example:**
```json
"my-new-agent": {
  "model": "opencode-go/minimax-m2.5",
  "maxTokens": 4096,
  "fallback_models": ["opencode-go/glm-5"]
}
```

### Rule 10: Document Changes
Update relevant documentation when modifying configs:

| Change Type | Update Required |
|-------------|----------------|
| New agent | OPENCODE_MANUAL.md agents table |
| Model change | OPENCODE_MANUAL.md model characteristics |
| Category change | OPENCODE_MANUAL.md categories table |
| Breaking change | README.md setup instructions |

## Emergency Procedures

### If You Accidentally Committed Secrets

**DO NOT PANIC. Follow these steps:**

1. **Immediately revoke the exposed credentials** (rotate API keys)

2. **Remove from git history:**
   ```bash
   # Remove file from all history
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch PATH_TO_FILE' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push (only exception to Rule 7)
   git push origin --force --all
   ```

3. **Or use BFG Repo-Cleaner:**
   ```bash
   bfg --replace-text passwords.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

4. **Document the incident** in commit message after cleanup

## Checklist for Agents

Before completing any task in this repository:

- [ ] No credentials in modified files
- [ ] JSON syntax validated
- [ ] Changes tested and working
- [ ] Commit message follows format (type: description)
- [ ] Documentation updated if needed
- [ ] Changes committed
- [ ] Changes pushed to origin/master
- [ ] Remote sync confirmed (git status shows clean)

## Quick Reference

```bash
# Pre-commit checks
git diff --cached | grep -i "api_key\|secret\|token\|password"
grep -v "^\s*//" omo.jsonc | python3 -c "import json,sys,re; json.loads(re.sub(r',(\s*[}]])', r'\1', sys.stdin.read()))" > /dev/null

# Commit template
git commit -m "type: short description

Detailed explanation

- What: <changes>
- Why: <reasoning>
- Tested: <verification>"

# Push
git push origin master
```

---

**Last updated:** 2026-04-01  
**Enforced by:** All AI agents working on this repository
