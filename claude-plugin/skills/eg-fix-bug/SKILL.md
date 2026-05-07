---
name: eg-fix-bug
description: Fix a bug using the elephant/goldfish workflow — problem doc, goldfish diagnosis check, failing test, fix, review, validate
argument-hint: bug description, GitHub issue URL, or symptom + repro
disable-model-invocation: true
---

Fix a bug using the elephant/goldfish workflow. The aim: write a problem doc, goldfish-check the diagnosis (so we are not anchored to the first hypothesis), capture the bug as a failing test, fix it, then run `/eg-precommit-review` and the test gate.

`$ARGUMENTS` is the bug description provided by the user. If empty, ask for one before doing anything. If `$ARGUMENTS` is a GitHub issue URL or `#<number>`, fetch it first with `gh issue view <number> --json title,body,labels,comments` and seed the problem doc from it.

## Step 0: Triviality gate

**Skip the goldfish/test ceremony for:** typo fixes in copy or comments, dead-code removal, version bumps, formatter-only diffs, single-line config tweaks. Go straight to Step 5 (`/eg-precommit-review`) and the test gate.

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

If the user gave no repro and the bug is not obvious from a single file read, **stop and ask** for a repro path (URL, steps, failing test name, log line, screenshot). Do NOT guess. The goldfish needs something concrete to act on.

**Browser / simulator validation.** Choose by the detected stack:

- **Web app** (look for `package.json` with a dev script, `vite.config`, `next.config`, `wrangler.jsonc`, etc.): use Chrome MCP (`mcp__Claude_in_Chrome__*`) against the dev URL. Find the URL from `package.json` scripts, `wrangler.jsonc`, README, or CLAUDE.md; common defaults are `http://localhost:3000`, `http://localhost:5173`, `https://localhost:4444`. Assume the dev server is running, or find the start command from `package.json` scripts (`npm run dev`, `pnpm dev`, etc.) or CLAUDE.md and start it. Navigate, click, screenshot, read the console.
- **Mobile** (Flutter `pubspec.yaml`, native iOS / Android): run on a simulator (`flutter run -d <device>`, `xcrun simctl`, `adb`) and capture screenshots / device logs. For layout-only bugs that reproduce on web, `flutter run -d chrome` plus Chrome MCP works.
- **Backend-only**: skip browser validation. Repro is usually a `curl` against the local server, a failing test name, or a log line.

## Step 2: Goldfish diagnosis check (parallel to your hypothesis)

Spawn a fresh agent with `Agent` tool:
- `subagent_type: "Explore"` for narrow lookups, `"general-purpose"` if the bug spans multiple subsystems. If the harness does not have `Explore` registered, fall back to `general-purpose`.
- `description: "Goldfish bug diagnosis"`

The goldfish gets ONLY the symptom + repro from Step 1. It does NOT get your hypothesised root cause — that asymmetry is the point.

**Prompt body to send (between markers, exclusive):**

```
<<<DIAG_START>>>
Independent diagnosis of a bug in this repo (this repo (read CLAUDE.md / README.md to identify the project name, stack, and one-line purpose; if neither file exists, derive from the manifests); CLAUDE.md at the repo root has the full architecture).

Symptom: <FILL IN from Step 1>
Repro: <FILL IN from Step 1>

Investigate. Where in the codebase is the bug most likely to live? Cite specific file:line locations. List the top 1-3 candidate root causes ranked by likelihood. For each candidate, name what evidence in the code supports it and what would falsify it. Do NOT propose a fix yet — just diagnose.

If a UI repro is needed, you may use the Chrome MCP (`mcp__Claude_in_Chrome__*`) against the running dev server, or run on a simulator for mobile. Backend-only repos: skip browser validation.."
- For mobile: omit this note; the goldfish reads code, not simulators.
- For backend-only: omit.]

End with the literal string `diagnosis complete`.
<<<DIAG_END>>>
```

**Compare goldfish output to your Step 1 hypothesis.**
- Convergence (top candidate matches your hypothesis): proceed to Step 3 with confidence.
- Divergence: re-investigate. Read the goldfish's evidence. If it is right, update the problem doc and tell the user "goldfish flagged a different root cause; re-diagnosing." If you are right, write down WHY the goldfish was wrong — that disagreement is itself useful signal.

If the bug is genuinely tiny (1-3 line fix in a clearly-identified location), you may skip the goldfish call — but only when the location is mechanically obvious. When in doubt, run it.

## Step 3: Capture the bug as a failing test BEFORE fixing

The verification criterion lives in code, not in chat. Pick the right tier:

**Pick the right test tier from the project's actual layout.** Common patterns:
- **Models / scopes / validations** → unit test next to the source (Rails `test/models/`, Flutter `test/`, Vitest `*.test.ts`).
- **Controllers / API endpoints** → controller test (`test/controllers/`, Grape API tests, FastAPI `TestClient`, Django views).
- **Workers / background jobs** → worker test (`test/workers/`, RQ tests, Celery tests).
- **UI flows / multi-screen / auth** → E2E (Playwright, Cypress, Capybara system tests).
- **Server-rendered page assertions** → Rails system tests, Django LiveServer.
- **Native UI / widget logic** → Flutter `WidgetTester`, Compose / SwiftUI snapshot.
Inspect the test directories that exist in the repo and pick the tier whose folder is the natural home for this fix.

Write the test. Run it. Confirm it fails for the reason described in the problem doc. If it fails for a different reason, the test is wrong — fix the test before touching the implementation.

For UI bugs where a Playwright/Cypress regression spec is overkill, capture the repro as a one-shot script in the conversation: navigate, click, screenshot, read console — and confirm the bug is observable. This is your verification path; you will re-run it after the fix.

## Step 4: Fix it

Implement the smallest change that turns the failing test green and matches the "Fixed means" criterion.

Avoid: adjacent refactors, defensive coding for cases the bug did not surface, fallbacks that mask future regressions, unrequested feature flags. Bug fix scope is the bug, nothing else.

Re-run the failing test. It must go green. If it does not, you have not fixed the bug — do NOT rewrite the test.

For UI bugs: re-verify in Chrome MCP / on the simulator with the same steps from the original repro. A before/after screenshot pair often helps the user follow.

## Step 5: Hand off to `/eg-precommit-review`

Run `/eg-precommit-review` per the canonical procedure. The reviewer is a second goldfish — it sees only the diff. Triage findings, loop, and exit.

If `/eg-precommit-review` surfaces an issue that the Step 2 diagnosis goldfish missed, note it in the final report — it tells us where the diagnosis prompt needs to be tighter next time.

## Step 6: Test gate

```sh
Run lint / typecheck / unit / E2E sequentially (NOT `&&`-chained — short-circuiting hides failures). Detect the actual commands from the manifests / CI config / CLAUDE.md as in the pre-flight detection rules. Skip tiers that don't apply for this stack (e.g. no separate typecheck step in Ruby; no E2E if there's no `e2e/` directory).
```

All required tiers must pass. Skip E2E only when the diff is purely model/worker/lib with no observable UI or API surface change. For bugs that touched generated code (e.g. `.g.dart`, protobuf), confirm regeneration ran and the generated files are committed. For UI bugs, also re-verify the original repro in Chrome MCP / on the simulator (whichever applies) one final time before reporting done.

## Step 7: Final report

Print to the user:
- Bug summary (one line)
- Root cause (one line)
- Fix (file:line)
- Test that captures it (file:test name)
- Goldfish-vs-elephant agreement (converged / diverged + why)
- `/eg-precommit-review` outcome (rounds, fixes, rebuttals verbatim)
- Test gate status

**STOP.** Do NOT commit; auto mode does not override the project's commit policy. Wait for the user's literal commit instruction. Follow the convention you observe in `git log` (subject style, ticket reference, trailers). Do not add `Co-Authored-By: Claude` unless the user's existing log already uses it.
