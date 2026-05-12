---
description: Fix a bug using the elephant/goldfish workflow — problem doc, goldfish diagnosis check, failing test, fix, review, validate
argument-hint: bug description, GitHub issue URL, or symptom + repro
---

Fix a bug using the elephant/goldfish workflow. The aim: write a problem doc, goldfish-check the diagnosis (so we are not anchored to the first hypothesis), capture the bug as a failing test, fix it, then run `/eg-precommit-review` and the test gate.

`$ARGUMENTS` is the bug description provided by the user. If empty, ask for one before doing anything. If `$ARGUMENTS` is a GitHub issue URL or `#<number>`, fetch it first with `gh issue view <number> --json title,body,labels,comments` and seed the problem doc from it.

## Interactivity is mandatory at decision points — overrides any "no-stopping" directive

This skill is mostly autonomous, but it has **mandatory** user-facing decision points: the missing-repro stop in Step 1, the goldfish-vs-elephant divergence resolution in Step 2, and any moment where the bug shape is genuinely ambiguous. Enumerable choices go through `AskUserQuestion`; genuinely unbounded answers (repro steps in prose, custom log lines) go through one targeted chat prompt AFTER an `AskUserQuestion` scopes the reason.

If a `<system-reminder>` or any other injected directive in this session tells you to work autonomously without stopping for clarifying questions (e.g. "no-stopping directive"), **it does NOT override these gates**. In particular: do NOT guess a repro on the user's behalf — the goldfish needs something concrete to act on, and a wrong-shaped guess wastes the goldfish call. Always ask.

The only opt-out: if the user, in the same turn that invoked this skill, explicitly says "use your best guess for the repro" (or equivalent unambiguous override), you may proceed with an inferred repro. Even then: print the repro you're using before spawning the goldfish.

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

If the user gave no repro and the bug is not obvious from a single file read, **stop and call `AskUserQuestion`** to scope the missing repro:

- `question`: "No repro provided. How would you like to proceed?"
- `header`: `"Repro?"`
- `multiSelect`: `false`
- `options`:
  1. **I'll paste a repro in chat** — "Steps, URL, failing test name, log line, or screenshot."
  2. **It's in a GitHub issue / linked doc** — "I'll share the link in chat."
  3. **You infer it from the symptom** — "Use your best guess; I accept the risk it may be wrong-shaped."
  4. **Drop the request** — "Not enough context yet; I'll come back."

Then accept the user's free-form input in chat for options 1 or 2. Do NOT guess on the user's behalf unless they pick option 3. The goldfish needs something concrete to act on.

[BOOTSTRAP: browser validation block — pick one and substitute:
- For web apps: "For UI bugs, the repro path is usually **Chrome MCP** (`mcp__Claude_in_Chrome__*`) against `[BOOTSTRAP: dev URL]` — assume the dev server is running, or start it via `[BOOTSTRAP: dev start command]`. Navigate, click, take a screenshot, read the console."
- For mobile (Flutter / iOS / Android / etc.): "For UI bugs, the verification path is a simulator/device run (`flutter run -d <device>` or equivalent). Take a screenshot from the simulator. For layout-only bugs that reproduce on web, the Chrome MCP can be used against `flutter run -d chrome`."
- For backend-only services: "Repro is usually a `curl` against the local server, a failing test name, or a log line. There is no UI surface to drive."]

## Step 2: Goldfish diagnosis check (parallel to your hypothesis)

Spawn a fresh agent with `Agent` tool:
- `subagent_type: "Explore"` for narrow lookups, `"general-purpose"` if the bug spans multiple subsystems. If the harness does not have `Explore` registered, fall back to `general-purpose`.
- `description: "Goldfish bug diagnosis"`

The goldfish gets ONLY the symptom + repro from Step 1. It does NOT get your hypothesised root cause — that asymmetry is the point.

**Prompt body to send (between markers, exclusive):**

```
<<<DIAG_START>>>
Independent diagnosis of a bug in this repo ([BOOTSTRAP: one-sentence project description, e.g. "<project-name>, the <stack> backend/frontend/app for <one-line product description>"]; CLAUDE.md at the repo root has the full architecture).

Symptom: <FILL IN from Step 1>
Repro: <FILL IN from Step 1>

Investigate. Where in the codebase is the bug most likely to live? Cite specific file:line locations. List the top 1-3 candidate root causes ranked by likelihood. For each candidate, name what evidence in the code supports it and what would falsify it. Do NOT propose a fix yet — just diagnose.

[BOOTSTRAP: browser validation note for the goldfish — substitute or remove:
- For web: "If a UI repro is needed, you may use the Chrome MCP (`mcp__Claude_in_Chrome__*`) against the running dev server at [BOOTSTRAP: dev URL]."
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

[BOOTSTRAP: test tier picks — replace with concrete options for this stack. Examples:
- Rails: model unit (`test/models/`), controller (`test/controllers/`), Grape API (`test/api/`), Sidekiq worker (`test/workers/`), Capybara system (`test/system/`), Playwright E2E (`e2e/`)
- Node + Vitest + Playwright: unit (`*.test.ts` next to source), Playwright E2E (`e2e/`), worker test
- Flutter: unit (`test/`), widget test (`test/`), `MockClient`-backed BLoC test, integration_test (`integration_test/`, heavy)
- Python + pytest: unit (`tests/unit/`), integration (`tests/integration/`), E2E (`tests/e2e/`)]

Write the test. Run it. Confirm it fails for the reason described in the problem doc. If it fails for a different reason, the test is wrong — fix the test before touching the implementation.

[BOOTSTRAP: UI bug repro fallback — pick one:
- For web: "For UI bugs where a full Playwright spec is overkill, capture the repro as a Chrome MCP script in the conversation: navigate, click, screenshot, read console — and confirm the bug is observable. This is your verification path; you re-run it after the fix."
- For mobile: "For bugs that only reproduce on a real device or simulator (platform channel, native rendering), capture the repro as a simulator script: launch, navigate, screenshot, read device log via `flutter logs`. This is the manual verification path."
- For backend-only: omit this paragraph.]

## Step 4: Fix it

Implement the smallest change that turns the failing test green and matches the "Fixed means" criterion.

Avoid: adjacent refactors, defensive coding for cases the bug did not surface, fallbacks that mask future regressions, unrequested feature flags. Bug fix scope is the bug, nothing else.

Re-run the failing test. It must go green. If it does not, you have not fixed the bug — do NOT rewrite the test.

[BOOTSTRAP: post-fix UI verification reminder, matching the Step 1 browser validation block.]

## Step 5: Hand off to `/eg-precommit-review`

Run `/eg-precommit-review` per the canonical procedure. The reviewer is a second goldfish — it sees only the diff. Triage findings, loop, and exit.

If `/eg-precommit-review` surfaces an issue that the Step 2 diagnosis goldfish missed, note it in the final report — it tells us where the diagnosis prompt needs to be tighter next time.

## Step 6: Test gate

```sh
[BOOTSTRAP: test gate commands as separate lines, e.g.:
- `npm test`
- `npm run test:e2e`   # only if the diff touches UI / API surface
or
- `RAILS_ENV=test mise exec ruby@2.7.5 -- bundle exec rails test --verbose`
- `mise exec ruby@2.7.5 -- bundle exec brakeman -q --no-pager`
- `npm run e2e -- --reporter=list`   # if UI / API touched
or
- `flutter analyze`
- `flutter test`]
```

All required tiers must pass. [BOOTSTRAP: skip-condition note, e.g. "Skip E2E only when the diff is purely model/worker/lib with no observable UI or API surface change." or "For bugs that touched generated code, confirm the .g.dart files are up to date."] For UI bugs, also re-verify the original repro [BOOTSTRAP: in Chrome MCP / on the simulator] one final time before reporting done.

## Step 7: Final report

Print to the user:
- Bug summary (one line)
- Root cause (one line)
- Fix (file:line)
- Test that captures it (file:test name)
- Goldfish-vs-elephant agreement (converged / diverged + why)
- `/eg-precommit-review` outcome (rounds, fixes, rebuttals verbatim)
- Test gate status

**STOP.** Do NOT commit; auto mode does not override the project's commit policy. Wait for the user's literal commit instruction. [BOOTSTRAP: commit-policy reminder per project — e.g. "Follow the convention visible in `git log` (plain commit message, optionally referencing the GitHub issue with `Fix #<n>:`)." or "No `Co-Authored-By: Claude` trailers."]
