---
name: eg-fix-bug
description: Fix a bug using the elephant/goldfish workflow — problem doc, independent goldfish diagnosis, failing test, fix, review, test gate. Use when the user asks to fix a bug, references a GitHub issue, or provides a symptom plus repro steps.
disable-model-invocation: true
---

Fix a bug using the elephant/goldfish workflow. The aim: write a problem doc, goldfish-check the diagnosis (so we are not anchored to the first hypothesis), capture the bug as a failing test, fix it, then run `/eg-precommit-review` and the test gate.

If the user provided a GitHub issue URL or `#<number>`, fetch it first via the `Shell` tool with `gh issue view <number> --json title,body,labels,comments` and seed the problem doc from it.

## Interactivity at decision points

This skill is mostly autonomous, but it has **mandatory** user-facing decision points: the missing-repro stop in Step 1, the goldfish-vs-elephant divergence resolution in Step 2, and any moment where the bug shape is genuinely ambiguous. Enumerable choices go through `AskQuestion`; genuinely unbounded answers (repro steps in prose, custom log lines) go through one targeted chat prompt AFTER an `AskQuestion` scopes the reason.

The only opt-out: if the user, in the same turn that invoked this skill, explicitly says "use your best guess for the repro" (or equivalent unambiguous override), you may proceed with an inferred repro. Even then: print the repro you're using before spawning the goldfish.

## Step 0: Triviality gate

**Skip the goldfish/test ceremony for:** typo fixes in copy or comments, dead-code removal, version bumps, formatter-only diffs, single-line config tweaks. Apply the requested trivial edit first. Then go to Step 5 (`/eg-precommit-review`) and the test gate; skip only the diagnosis and failing-test ceremony.

**Run the full loop for everything else,** including small one-line code fixes — small diffs hide bugs disproportionately well.

## Step 1: Write the problem doc (in this conversation)

Print a tight problem doc to the user. Keep it brief but complete:

```
PROBLEM DOC
- Symptom: <what the user observes>
- Repro: <steps to reproduce, or "user did not provide; need to derive">
- Suspected area: <file/module/route/worker/job/screen>
- Hypothesised root cause: <one sentence>
- Blast radius: <which other surfaces could be affected>
- "Fixed" means: <specific test passes / specific behavior / specific output>
```

If the user gave no repro and the bug is not obvious from a single file read, **stop and call `AskQuestion`** to scope the missing repro:

- `prompt`: "No repro provided. How would you like to proceed?"
- `options`:
  1. **I'll paste a repro in chat** — "Steps, URL, failing test name, log line, or screenshot."
  2. **It's in a GitHub issue / linked doc** — "I'll share the link in chat."
  3. **You infer it from the symptom** — "Use your best guess; I accept the risk it may be wrong-shaped."
  4. **Drop the request** — "Not enough context yet; I'll come back."

Then accept the user's free-form input in chat for options 1 or 2. Do NOT guess on the user's behalf unless they pick option 3. The goldfish needs something concrete to act on.

[BOOTSTRAP: browser validation block — pick one and substitute:
- For web apps: "For UI bugs, the repro path is usually Cursor's built-in `browser` subagent (Browser MCP) against `[BOOTSTRAP: dev URL]` — assume the dev server is running, or start it via `[BOOTSTRAP: dev start command]`. Navigate, click, take a screenshot, read the console."
- For mobile (Flutter / iOS / Android / etc.): "For UI bugs, the verification path is a simulator/device run (`flutter run -d <device>` or equivalent). Take a screenshot from the simulator. For layout-only bugs that reproduce on web, the `browser` subagent can be used against `flutter run -d chrome`."
- For backend-only services: "Repro is usually a `curl` against the local server, a failing test name, or a log line. There is no UI surface to drive."]

## Step 2: Goldfish diagnosis check (parallel to your hypothesis)

Spawn a fresh agent using the `Task` tool:
- `subagent_type: "explore"` for narrow lookups; `"generalPurpose"` if the bug spans multiple subsystems.
- `description: "Goldfish bug diagnosis"`

The goldfish gets ONLY the symptom + repro from Step 1. It does NOT get your hypothesised root cause.

**Prompt body to send via the `Task` tool's `prompt` parameter:**

```
Independent diagnosis of a bug in this repo ([BOOTSTRAP: one-sentence project description]; AGENTS.md / CLAUDE.md at the repo root has the full architecture).

Symptom: <FILL IN from Step 1>
Repro: <FILL IN from Step 1>

Investigate. Where in the codebase is the bug most likely to live? Cite specific file:line locations. List the top 1-3 candidate root causes ranked by likelihood. For each candidate, name what evidence in the code supports it and what would falsify it. Do NOT propose a fix yet — just diagnose.
```

**Compare goldfish output to your Step 1 hypothesis.**
- Convergence: proceed to Step 3 with confidence.
- Divergence: re-investigate. Update the problem doc if the goldfish is right. Surface the divergence to the user before fixing.

## Step 3: Capture the bug as a failing test BEFORE fixing

The verification criterion lives in code, not in chat. Pick the right tier:

[BOOTSTRAP: test tier picks — replace with concrete options for this stack, e.g.:
- Rails: "model test under `test/models/`, controller test under `test/controllers/`, system test under `test/system/`."
- Flutter: "unit test under `test/`, widget test under `test/widget/`, integration test under `integration_test/`."
- Node + Vitest: "unit under `tests/unit/`, integration under `tests/integration/`, Playwright e2e under `e2e/`."
- Etc.]

Write the test using `Write` or `StrReplace`. Run it via the `Shell` tool. Confirm it fails for the reason described in the problem doc. If it fails for a different reason, fix the test before touching the implementation.

[BOOTSTRAP: UI bug repro fallback — pick one:
- For web apps: "If the bug only reproduces interactively, capture it via the `browser` subagent (screenshot + console snippet) as a 'bug evidence' attachment in chat, then write the failing automated test against the same condition."
- For mobile: "If the bug only reproduces on a real device, capture a screenshot + reproduce notes in chat, then write the failing automated test against the same condition."
- For backend: "If the bug only reproduces under load or a specific payload, capture the payload in a test fixture and assert on it."]

## Step 4: Fix it

Implement the smallest change that turns the failing test green and matches the "Fixed means" criterion using `StrReplace` or `Write`.

Avoid adjacent refactors. Bug fix scope is the bug, nothing else.

Re-run the failing test. It must go green.

## Step 5: Hand off to `/eg-precommit-review`

Run the `eg-precommit-review` skill explicitly. The reviewer is itself a goldfish (see that skill); it gets only the diff, not the conversation. Findings are triaged round by round, with a hard cap and a structured user escalation if the loop doesn't converge.

## Step 6: Test gate

Execute the test gate via the `Shell` tool:

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
- Goldfish-vs-elephant agreement (convergent / divergent — and if divergent, how it was resolved)
- Test gate status

**STOP.** Do NOT commit. Wait for the user's literal commit instruction. [BOOTSTRAP: commit-policy reminder per project.]
