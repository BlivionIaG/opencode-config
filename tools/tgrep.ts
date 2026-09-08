// Custom tool: tgrep
//
// Wraps Microsoft's tgrep CLI (https://github.com/microsoft/tgrep) — a
// trigram-indexed grep with a client/server architecture for fast regex
// search in large codebases. Lives alongside the built-in `grep` tool;
// agents pick whichever they want.
//
// Invocation:
//   - If a `tgrep serve` is running on the target directory, this tool
//     connects to it and queries the in-memory overlay.
//   - Otherwise tgrep auto-builds an index or falls back to brute force
//     (`--no-index`), so the tool always returns *something* usable.
//   - Output formatting follows the default tgrep human format. Add
//     `--json` / `--vimgrep` style flags via the `extraArgs` field.

import { tool } from "@opencode-ai/plugin"

const TGREP_BIN = "/Users/kletorch/.cargo/bin/tgrep"

export default tool({
  description:
    "Trigram-indexed grep (microsoft/tgrep). Faster than ripgrep on large repos (388k-file gecko-dev: ~52x). Use for regex search across a codebase. Connects to a running `tgrep serve` if one is up; otherwise auto-builds an index. Use `extraArgs` to pass tgrep flags (e.g. `-i`, `-l`, `-n`, `--json`, `--no-index`).",

  args: {
    pattern: tool.schema
      .string()
      .describe(
        "Regex pattern to search for. tgrep uses its own regex engine by default; pass 'PCRE-style' with `extraArgs: ['--engine', 'pcre2']` for lookaround/backrefs.",
      ),
    path: tool.schema
      .string()
      .optional()
      .describe(
        "Directory or file to search. Defaults to the session working directory (context.directory).",
      ),
    extraArgs: tool.schema
      .array(tool.schema.string())
      .optional()
      .describe(
        "Extra tgrep CLI flags, e.g. ['-i', '-l', '-n', '--json', '--no-index', '-C', '3'].",
      ),
  },

  async execute(args, context) {
    const searchPath = args.path ?? context.directory
    const argv = [TGREP_BIN, args.pattern, searchPath]
    if (args.extraArgs && args.extraArgs.length > 0) {
      argv.push(...args.extraArgs)
    }

    const proc = Bun.spawn(argv, {
      stdout: "pipe",
      stderr: "pipe",
    })

    const [stdout, stderr, exitCode] = await Promise.all([
      new Response(proc.stdout).text(),
      new Response(proc.stderr).text(),
      proc.exited,
    ])

    if (exitCode !== 0) {
      const err = stderr.trim() || `(tgrep exited with code ${exitCode})`
      throw new Error(`tgrep failed: ${err}`)
    }

    return stdout
  },
})