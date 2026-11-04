# Elephant/Goldfish

A small workflow harness for Claude Code, Codex, Gemini CLI, Cursor and Grok Build.
Your main session keeps the context. Fresh agents review a problem, design or diff
without inheriting the conversation that produced it. That second view helps catch
assumptions the first agent has stopped questioning.

Based on [Dave Rensin's elephant/goldfish article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874).
Recent additions come from my [ClaudeFlows](https://github.com/OmniPragmatic/claudeflows)
work: short question flows, PRD task handoffs and reviews that survive compaction.
It costs extra time and tokens. Use it where a second opinion is worth that cost.

## Pick a workflow

| Command | What it does |
|---|---|
| `eg-question` | Answers a codebase or technical question with citations. Read-only. |
| `eg-brainstorm` | Explores different approaches to a rough idea. |
| `eg-prd` | Turns an idea into requirements, with optional tasks for later sessions. |
| `eg-new-feature` | Reviews a design before building, then reviews and tests the result. |
| `eg-fix-bug` | Gets an independent diagnosis, captures the failure, then fixes it. |
| `eg-precommit-review` | Reviews staged, unstaged and untracked changes separately. |

Start wherever you are. You don't need a PRD to fix a bug or review a diff.
Reviews report gaps and rebuttals explicitly. They don't silently commit your work.
If a host can't start fresh agents, the workflow reports that limitation.

## Install

In your project, ask your agent to run the appropriate bootstrap:

| Agent | Adapter | Installed location | Invoke |
|---|---|---|---|
| Claude Code | `claude` | `.claude/commands/` | `/eg-question ...` |
| Codex | `codex` | `${CODEX_HOME:-~/.codex}/skills/` | `Use $eg-question ...` |
| Gemini CLI | `gemini` | `.gemini/skills/` | Ask to use `eg-question` |
| Cursor | `cursor` | `.cursor/skills/` | `/eg-question ...` |
| Grok Build | `grok` | `.grok/skills/` | `/eg-question ...` |

Replace `<adapter>` with the value above and paste this into your agent:

```text
Fetch `gh api repos/vshvedov/elephant-goldfish/contents/<adapter>/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'`
and follow it to install elephant/goldfish here. Preserve my existing customizations
and other agents' setups.
```

This uses the [GitHub CLI](https://cli.github.com/). Start a new agent session after
installation. In Gemini, use `/skills reload`. In Grok, `grok inspect --json` shows
which skills were found after you trust the project folder. The adapters can coexist; Codex skills are shared across
projects, while the others are project-local.

## Use it

```text
/eg-question Where is access to this endpoint checked?
/eg-fix-bug The cache returns another tenant's result after switching accounts.
/eg-precommit-review
```

For work split across sessions, `eg-prd` can produce a numbered roadmap. Pick one task:

```text
/eg-new-feature implement T2 from docs/prds/export.md
```

In Codex, use `Use $eg-new-feature to implement T2 from docs/prds/export.md`.
The workflow checks prerequisites, carries the task's scope into the design and
suggests the next task after validation. It doesn't start the next task on its own.

For updates, use the [update prompt](PROMPTS.md). Installation compares changes
before replacing files so project-specific commands and edits survive.

[Changes and comparison](docs/claudeflows-port.md) · [Testing](docs/testing.md) · [MIT license](LICENSE)
