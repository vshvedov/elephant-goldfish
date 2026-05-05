---
description: Run a Codex-native pre-commit independent-review loop on pending changes.
---

# EG Precommit Review

Run the pre-commit review loop. The goal is to validate pending changes locally before commit with a fresh reviewer that sees the diff cold.

If `$ARGUMENTS` is non-empty, treat it as an additional focus area for the reviewer.

## Preflight

Skip the loop for pure documentation-only commits, typo-only edits, version bumps, dependency updates with no code changes, formatter-only diffs, and merge commits.

Run it for everything else.

Run these checks sequentially, not chained:

```sh
[BOOTSTRAP: lint command]
```

[BOOTSTRAP: typecheck block — include if separate typechecking exists:
```sh
[BOOTSTRAP: typecheck command]
```
]

```sh
[BOOTSTRAP: unit test command]
```

[BOOTSTRAP: e2e test block — include if E2E exists:
```sh
[BOOTSTRAP: e2e test command]
```
Skip only when the diff is purely [BOOTSTRAP: layers that do not need E2E].
]

[BOOTSTRAP: code-generation block — include if applicable:
If the diff modifies [BOOTSTRAP: regeneration trigger], regenerate first:
```sh
[BOOTSTRAP: codegen command]
```
Both source and generated files must be committed together.
]

New errors introduced by the diff are blockers. Pre-existing failures are out of scope; if needed, baseline against `main` and compare outputs.

## Goldfish Review

The user invoked this command, so fresh subagent review is explicitly authorized.

Preferred path: spawn a fresh Codex subagent with `fork_context: false` and `agent_type: "default"`. If `spawn_agent` is unavailable, pipe the reviewer prompt into the Codex CLI fallback:

```sh
codex review --uncommitted --base main -
```

Pass only the reviewer prompt below. Do not include the implementation plan, the original request, or explanatory context.

```
Independent code review of the pending changes on this branch.

Run all of the following to capture pending changes:
- `git status`
- `git diff`
- `git diff --cached`
- `git diff main...HEAD`
- `git log main..HEAD --oneline`
- `git ls-files --others --exclude-standard`

Read touched files in full where the diff context is not enough.

Find substantive issues. For each finding: cite file:line, name the issue, explain why it is a bug or risk, and suggest a concrete fix.

Hunt for:
- Bugs: off-by-ones, null/undefined dereference, wrong variable used, type coercion gotchas, unhandled promises, missing await, mutating function args, wrong return on error paths.
- Security: command injection, XSS, SQL injection, path traversal, prototype pollution, unsanitized input, secrets in URLs or logs, missing auth checks, missing CSRF, open redirects, IDOR.
- Race conditions: shared state without locks, async ordering, double-submit, event handler re-entry, TOCTOU.
- Edge cases: empty arrays, NaN, Infinity, zero, negative numbers, very large numbers, Unicode, timezone, network failure, partial writes.
- Error handling: silent catches, swallowed errors, fallback paths that mask real failures, missing propagation.
- Performance: N+1 queries, sync work in hot loops, missing memoization, layout thrashing, unbounded growth, missing pagination.
- Test coverage gaps, especially missing regression tests for bug fixes.
[BOOTSTRAP: stack-specific Hunt for items]
- Project-rule violations from AGENTS.md or CLAUDE.md, with citations.
- Dead code, leftover debug output, stale comments referencing removed code.

Do not surface style preferences, micro-refactors, or speculative concerns without a concrete failure mode.

[NO ADDITIONAL FOCUS]

Output format: numbered list. For each finding, lead with file:line. End with the literal string `no findings` if and only if the diff is clean.
```

If `$ARGUMENTS` is non-empty, replace `[NO ADDITIONAL FOCUS]` with `Additionally focus on: <$ARGUMENTS verbatim>`.

## Triage

For each finding:

- Fix it, noting the file:line touched.
- Or rebut it with one line: `not a bug because ...`, `out of scope because ...`, `intentional trade-off documented in ...`, or `user explicitly asked for this: "..."`

Surface every rebuttal verbatim in the final report.

## Loop

Before each new round, print:

```text
Open findings going into round N:
- [from round 1] file:line — fixed
- [from round 1] file:line — rebutted: <verbatim reason>
```

Run another fresh goldfish review with the same prompt plus:

```text
Previous round's fixes:
- file:line — what changed

Verify each fix is correct and complete. Look for anything missed in the first pass, especially issues introduced by the fixes.
```

Stop when the reviewer returns `no findings` and all prior findings are fixed or rebutted.

Hard cap: 5 rounds. If the cap trips, summarize open findings and ask the user whether to accept, keep working, or abandon.

## Final Report

Report:

- Rounds run
- Findings fixed
- Findings rebutted verbatim
- Pre-existing lint/typecheck/test failures treated as out of scope

Stop short of staging or committing. [BOOTSTRAP: commit policy reminder]
