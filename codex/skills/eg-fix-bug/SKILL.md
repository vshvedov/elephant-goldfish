---
name: "eg-fix-bug"
description: Fix a bug with Codex using problem doc, independent diagnosis, failing test, fix, review, and validation.
---

# EG Fix Bug Skill

Fix a bug using the elephant/goldfish workflow. Use the user's text around the `$eg-fix-bug` skill mention as the bug description. If no description is provided, ask for one.

If the bug description is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number> --json title,body,labels,comments` and seed the problem doc from it.

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

For UI bugs, use the project-appropriate manual verification path. Prefer Browser Use / the in-app browser for web apps, a simulator/device run for mobile apps, and curl/log/test reproduction for backend-only services. Start or identify the dev server from package scripts, AGENTS.md/CLAUDE.md, or CI docs when needed.

## Goldfish Diagnosis

The user invoked this skill, so a fresh diagnosis subagent is explicitly authorized.

Spawn a fresh Codex subagent with `fork_context: false`. Use `agent_type: "explorer"` for narrow codebase lookup when available; otherwise use default.

Send only the symptom and repro, not the elephant's hypothesized root cause:

```text
Independent diagnosis of a bug in this repo. AGENTS.md and CLAUDE.md may contain architecture notes.

Symptom: <FILL IN>
Repro: <FILL IN>

Investigate. Where is the bug most likely to live? Cite file:line locations. List the top 1-3 candidate root causes ranked by likelihood. For each, name supporting evidence and what would falsify it. Do not propose a fix yet.

If UI repro is needed, use the project-appropriate browser/simulator path only if available and safe.

End with `diagnosis complete`.
```

Compare the goldfish output to your hypothesis. If it diverges and the goldfish has better evidence, update the problem doc and re-diagnose. If your hypothesis is still better, write down why.

## Failing Test

Capture the bug as a failing test before fixing.

Choose the narrowest test tier that captures the bug. Infer test locations and commands from AGENTS.md, CLAUDE.md, package manifests, framework conventions, and CI config.

Run the new test and confirm it fails for the reason in the problem doc. If it fails for a different reason, fix the test before touching implementation.

For UI bugs where a full automated test is disproportionate, capture the repro as a manual verification script in the conversation: navigate, act, screenshot/log/console, and confirm the bug is observable. Re-run it after the fix.

## Fix

Implement the smallest change that makes the failing test green and matches "Fixed means." Avoid adjacent refactors and unrequested fallbacks.

Re-run the failing test. It must pass.

For UI bugs, re-run the original browser/simulator/manual repro after the code-level fix passes.

## Review

Use `$eg-precommit-review <bug summary>` or apply the same review procedure from the `eg-precommit-review` skill.

## Test Gate

Run:

```sh
<derive from AGENTS.md, CLAUDE.md, package manifests, and CI config>
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

Stop short of staging or committing. Follow the commit policy documented in AGENTS.md/CLAUDE.md if the user later asks to commit.
