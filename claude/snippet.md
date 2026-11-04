## Working with Claude Code (elephant/goldfish)

Use these workflows when explicitly requested. Don't start another workflow for
follow-ups inside work already in progress. Trivial questions and edits need no
multi-agent ceremony. Skills live in `.claude/commands`.

| Workflow | Use it for |
|---|---|
| `/eg-question` | A short answer grounded in code or sources. Read-only. |
| `/eg-brainstorm` | Different approaches to a rough idea. |
| `/eg-prd` | Requirements, open questions and optional session-sized tasks. |
| `/eg-new-feature` | Design, fresh reviews, implementation and checks. |
| `/eg-fix-bug` | Independent diagnosis, a failing regression test and a fix. |
| `/eg-precommit-review` | An independent review of staged, unstaged and untracked changes. |

The main session keeps context. Fresh reviewers receive only the evidence for
their task, with no implementation conversation. Missing dispatch or evidence
means incomplete, not a clean review. Check actual host capabilities before use.
Ask concise questions only for missing information or consequential choices.
Respect existing authorization; never stage, commit or push without it.
