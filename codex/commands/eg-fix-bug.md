---
description: Fix a bug with Codex using problem doc, independent diagnosis, failing test, fix, review, and validation.
---

# EG Fix Bug

Fix a bug using the elephant/goldfish workflow. `$ARGUMENTS` is the bug description. If empty, ask for one.

If `$ARGUMENTS` is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number> --json title,body,labels,comments` and seed the problem doc from it.

## Triviality Gate

Skip the goldfish/test ceremony for typo fixes in copy/comments, dead-code removal, version bumps, formatter-only diffs, and single-line config tweaks. Still run `eg-precommit-review` and the test gate.

Run the full loop for everything else.

## Problem Doc

Print:

```text
PROBLEM DOC
- Symptom: <what the user observes>
- Repro: <steps, failing test, URL, log, screenshot, or "need to derive">
- Suspected area: <file/module/route/job/screen>
- Hypothesized root cause: <one sentence>
- Blast radius: <surfaces that could be affected>
- Fixed means: <specific test/behavior/output>
```

If there is no repro and the bug is not obvious from a single file read, stop and ask for a concrete repro path.

[BOOTSTRAP: browser validation block]

## Goldfish Diagnosis

The user invoked this command, so a fresh diagnosis subagent is explicitly authorized.

Spawn a fresh Codex subagent with `fork_context: false`. Use `agent_type: "explorer"` for narrow codebase lookup when available; otherwise use default.

Send only the symptom and repro, not the elephant's hypothesized root cause:

```text
Independent diagnosis of a bug in this repo ([BOOTSTRAP: project description]). AGENTS.md and CLAUDE.md may contain architecture notes.

Symptom: <FILL IN>
Repro: <FILL IN>

Investigate. Where is the bug most likely to live? Cite file:line locations. List the top 1-3 candidate root causes ranked by likelihood. For each, name supporting evidence and what would falsify it. Do not propose a fix yet.

[BOOTSTRAP: browser validation note for diagnosis]

End with `diagnosis complete`.
```

Compare the goldfish output to your hypothesis. If it diverges and the goldfish has better evidence, update the problem doc and re-diagnose. If your hypothesis is still better, write down why.

## Failing Test

Capture the bug as a failing test before fixing.

[BOOTSTRAP: test tier picks]

Run the new test and confirm it fails for the reason in the problem doc. If it fails for a different reason, fix the test before touching implementation.

[BOOTSTRAP: UI repro fallback]

## Fix

Implement the smallest change that makes the failing test green and matches "Fixed means." Avoid adjacent refactors and unrequested fallbacks.

Re-run the failing test. It must pass.

[BOOTSTRAP: post-fix UI verification reminder]

## Review

Run `/elephant-goldfish-codex:eg-precommit-review <bug summary>` or apply the same review procedure from `eg-precommit-review.md`.

## Test Gate

Run:

```sh
[BOOTSTRAP: test gate commands]
```

All required tiers must pass. For UI bugs, re-verify the original repro through Browser Use / in-app browser or simulator.

## Final Report

Report:

- Bug summary
- Root cause
- Fix location
- Regression test
- Goldfish-vs-elephant agreement or divergence
- Review outcome, including verbatim rebuttals
- Test gate status

Stop short of staging or committing. [BOOTSTRAP: commit policy reminder]
