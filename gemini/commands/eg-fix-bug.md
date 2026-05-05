---
name: eg-fix-bug
description: Fix a bug using the elephant/goldfish workflow. Enforces a problem doc, goldfish diagnosis check, failing test, fix, and test gate.
---

Fix a bug using the elephant/goldfish workflow. The aim: write a problem doc, goldfish-check the diagnosis (so we are not anchored to the first hypothesis), capture the bug as a failing test, fix it, then run the test gate.

If the user provided a GitHub issue URL or `#<number>`, fetch it first with `run_shell_command` using `gh issue view <number> --json title,body,labels,comments` and seed the problem doc from it.

## Step 0: Triviality gate

**Skip the goldfish/test ceremony for:** typo fixes in copy or comments, dead-code removal, version bumps, formatter-only diffs, single-line config tweaks. Go straight to Step 5 (review/test gate).

**Run the full loop for everything else.**

## Step 1: Write the problem doc (in this conversation)

Print a tight problem doc to the user:

```
PROBLEM DOC
- Symptom: <what the user observes>
- Repro: <steps to reproduce, or "user did not provide; need to derive">
- Suspected area: <file/module/route/worker/job/screen>
- Hypothesised root cause: <one sentence>
- Blast radius: <which other surfaces could be affected>
- "Fixed" means: <specific test passes / specific behavior / specific output>
```

If the user gave no repro and the bug is not obvious, **stop and ask** for a repro path. Do NOT guess.

[BOOTSTRAP: browser validation block — pick one and substitute:
- For web apps: "For UI bugs, the repro path usually involves navigating the web app at `[BOOTSTRAP: dev URL]`. Assume the dev server is running, or start it via `[BOOTSTRAP: dev start command]`."
- For mobile: "For UI bugs, the verification path is a simulator/device run (`flutter run -d <device>` or equivalent)."
- For backend-only services: "Repro is usually a `curl` against the local server, a failing test name, or a log line."]

## Step 2: Goldfish diagnosis check

Spawn a fresh agent with `invoke_agent` (`agent_name="generalist"` or `"codebase_investigator"`):

The goldfish gets ONLY the symptom + repro from Step 1. It does NOT get your hypothesised root cause.

**Prompt body to send:**

```
Independent diagnosis of a bug in this repo ([BOOTSTRAP: one-sentence project description]; GEMINI.md at the repo root has the full architecture).

Symptom: <FILL IN from Step 1>
Repro: <FILL IN from Step 1>

Investigate. Where in the codebase is the bug most likely to live? Cite specific file:line locations. List the top 1-3 candidate root causes ranked by likelihood. For each candidate, name what evidence in the code supports it and what would falsify it. Do NOT propose a fix yet — just diagnose.
```

**Compare goldfish output to your Step 1 hypothesis.**
- Convergence: proceed to Step 3 with confidence.
- Divergence: re-investigate. Update the problem doc if the goldfish is right.

## Step 3: Capture the bug as a failing test BEFORE fixing

The verification criterion lives in code, not in chat. Pick the right tier:

[BOOTSTRAP: test tier picks — replace with concrete options for this stack.]

Write the test using `write_file` or `replace`. Run it via `run_shell_command`. Confirm it fails for the reason described in the problem doc. If it fails for a different reason, fix the test before touching the implementation.

[BOOTSTRAP: UI bug repro fallback — pick one.]

## Step 4: Fix it

Implement the smallest change that turns the failing test green and matches the "Fixed means" criterion using `replace` or `write_file`.

Avoid adjacent refactors. Bug fix scope is the bug, nothing else.

Re-run the failing test. It must go green.

## Step 5: Hand off to review

Run the `eg-precommit-review` workflow explicitly if the user requested a review, or review your own diff critically.

## Step 6: Test gate

Execute the test gate via `run_shell_command`:

```sh
[BOOTSTRAP: test gate commands as separate lines, e.g.:
- `npm test`
- `npm run test:e2e`
]
```

All required tiers must pass.

## Step 7: Final report

Print to the user:
- Bug summary (one line)
- Root cause (one line)
- Fix (file:line)
- Test that captures it (file:test name)
- Goldfish-vs-elephant agreement
- Test gate status

**STOP.** Do NOT commit. Wait for the user's literal commit instruction. [BOOTSTRAP: commit-policy reminder per project.]