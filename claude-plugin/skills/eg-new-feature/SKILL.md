---
name: eg-new-feature
description: Build a new feature using the elephant/goldfish workflow — design doc, goldfish design check, implement, review, validate
argument-hint: feature description (what the user wants and why)
disable-model-invocation: true
---

Build a new feature using the elephant/goldfish workflow. The aim: design before code, let a fresh goldfish stress-test the design doc, then implement, review, and validate.

`$ARGUMENTS` is the feature description provided by the user. If empty, ask for one before doing anything. If `$ARGUMENTS` is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number> --json title,body,labels,comments` and seed the design doc from it.

**Routing.** Before designing, scan the project's `.claude/commands/` for stack-specific verbs (e.g. `/eg-new-module`, `/eg-new-migration`, `/eg-new-worker`). If the user's request maps cleanly to one of those, suggest it instead. This skill covers everything else.

## Step 0: Confirm scope before designing

Restate the request back to the user in 1-2 sentences ("I read this as: <X>. Confirm or correct."). Misreads at this stage waste the most time later. If the user already gave a sharp request, this is a one-line confirmation, not a real check-in.

**Priority sanity-check.** If CLAUDE.md or a top-level docs file calls out current priorities / phases, honour them: green-light surfaces matching the documented focus, ask the user to confirm before proceeding on out-of-phase or future-phase work.

**Surface-area check.** Identify the layers this feature touches by reading the manifests and existing folder layout. Categories to consider, depending on stack: new screen / UI flow, new BLoC or service or VM, network / API change, schema / migration (and whether it bumps a Drift `schemaVersion`, an Active Record migration, or a Sequel migration), platform-specific work (iOS / Android / macOS / web), caching / invalidation, multi-tenant scoping, auth / authorization, background jobs / Sidekiq, observability / instrumentation. Flag the ones that apply.

## Step 1: Write the design doc

Print the design doc to the user. For most features this lives in chat; for substantial features (new domain area, new API resource family, new subsystem) propose writing it to the project's docs directory (`docs/` if it exists, otherwise `doc/`, otherwise propose creating one and ask) and ask the user before creating the file.

Required sections:

```
DESIGN DOC
- Why: <user problem this solves; cite GH issue, conversation, or PRD section>
- Scope: <what is in; what is explicitly out>
- Surfaces touched: <files / routes / models / controllers / components / DB tables / external services>
- Interfaces: <component props, function signatures, API request/response shapes, DB columns, queue arguments>
- UX flow: <click-by-click for UI; request-by-request for backend>
Append stack-specific fields where they apply: multi-tenant scoping, CanCanCan abilities, COEP/COOP headers and SharedArrayBuffer requirements, BLoC / stream lifecycle, schema migration version bump, authorization rules, rate limits, or any field the design needs that's specific to the detected stack.
- Failure modes: <what the user sees when each thing breaks; what the API returns>
- Verification criteria: <unit tests, E2E spec, project-specific test artifacts (e.g. tap-in patches, integration_test scripts, fixture seeds), manual Chrome MCP / simulator (whichever applies) steps>
- Out-of-scope follow-ups: <noted, not built>
```

If the project has PRD-driven discipline (look for `docs/prds/`, `docs/specs/`, or PRDs referenced from CLAUDE.md), **reference PRD section numbers** ("implements PRD §6.2") so the design doc and the PRD stay aligned.

For UI work, sketch the visual structure in plain text or pseudo-JSX. If the design needs a real visual reference, ask the user to point at an existing component to mirror.

### No-code gate

**Do NOT edit, write, scaffold, or refactor code until BOTH Pass B (Critic) AND Pass C (Readiness) in Step 2 close with their ready tokens (`design ready` + `implementation ready`).** Article rule, paraphrased: *"I do not want you to create code. We are not going to create code. Resist your impulse."* This holds until the design doc passes both gates — even if the user asks to skip ahead, even if the change "looks trivial", even if it is "just one line".

If the user explicitly asks to skip the gate ("just write the code", "skip the design doc", etc.), restate the gate, name the still-open passes, and require an explicit override ("yes, override the no-code gate") before touching any file outside the design doc itself. The exception is `/eg-fix-bug` for trivial fixes covered by its own Step 0 triviality gate — that is a separate command with a separate gate.

The design doc itself, test names mentioned in chat (not yet on disk), and read-only exploration (`Read`, `Grep`, `Bash` for `git status` / `git log` / `git diff`, any other read-only inspection commands the stack uses, e.g. `bundle exec rails routes`, `flutter analyze --no-pub`, `npx wrangler types`, `go doc ./...`) are NOT code edits and are permitted.

## Step 2: Three-goldfish design check

Run the article's full design-stage protocol: three sequential `Agent` calls per round (or two on revisions — see below), each with no prior context. The combined gate is "ready iff critic AND readiness both sign off"; comprehension is informational.

Each pass uses `subagent_type: "general-purpose"` and gets ONLY the design doc (no chat history, no implementation intent, no other passes' output). The asymmetry is the value.

**Round 1 runs all three passes; round 2+ skips comprehension** (revisions are gap-driven, not structural — once the doc reads cleanly, it almost always still reads cleanly). On every round, run critic and readiness.

### Pass A — Comprehension (round 1 only)

`description: "Goldfish comprehension check"`. Verifies the doc reads cleanly to a cold reader.

```
<<<COMPREHENSION_START>>>
You are a fresh reader with no prior context. Below is a design doc for a feature in the this repo (project name and stack derived from CLAUDE.md / README / manifests) repo. Do NOT critique it yet. Your job is to verify the doc reads clearly to someone who walks in cold.

Output two short sections in this order:

## What this feature does
2-5 sentences in your own words. The user-visible change. Who triggers it, when, what they get back.

## How the existing system works (per the doc)
2-5 sentences summarizing the current behavior the doc describes touching. Surfaces, controllers, components, message flow — whatever the doc references.

End your output with EXACTLY one of these closing lines, on its own line:
- comprehension passed       (the doc reads cleanly; no ambiguous sections)
- comprehension unclear      (one or more sections are too vague to paraphrase)

If you mark it unclear, list the ambiguous sections by heading before the closing line. Do NOT critique architecture choices here — that is the critic's job. Only flag things you genuinely cannot understand.

DESIGN DOC:

<PASTE FULL DESIGN DOC FROM STEP 1 HERE>
<<<COMPREHENSION_END>>>
```

### Pass B — Critic (every round)

`description: "Goldfish design critic"`. Finds gaps that block implementation.

```
<<<DESIGN_START>>>
You are a fresh reviewer with no prior context. Below is a design doc for a feature in the this repo (project name and stack derived from CLAUDE.md / README / manifests) repo (CLAUDE.md at the repo root has the architecture, including any architectural invariants documented in CLAUDE.md (multi-tenancy, lifecycle, schema migrations, real-time / audio constraints, etc.)).

Your job: read the design doc, then read the surfaces it claims to touch, and find holes BEFORE implementation starts. Specifically:

- Is the scope crisp? What questions would you have to answer to implement this that the doc does not answer?
- Are the interfaces concrete enough that two implementers would converge on the same result?
- Do the verification criteria actually verify the feature, or only verify that "something rendered"?
- Does the doc misunderstand any existing code? Look up the surfaces it claims to touch and check.
- Are there failure modes the doc missed? Network errors, unauthenticated users, empty state, partial saves, stale data, retries.
Append stack-specific gap items where they apply: multi-tenant scoping consistency, lifecycle / dispose paths, BLoC stream cleanup, COEP / SharedArrayBuffer regression risk, audio-thread allocation invariants, frozen-module-set policies, RC / staging dependencies. Pick the items that fit the detected stack.
- Are there project-specific gotchas the doc ignores? CLAUDE.md is your reference.

If the project has a PRD relevant to this surface (look in `docs/prds/`, `docs/specs/`, or referenced from CLAUDE.md), load it and check that the design doc is consistent with it.

For UI work, the goldfish may navigate the running dev server via Chrome MCP (`mcp__Claude_in_Chrome__*`) at the project's dev URL to verify how an existing surface behaves. Backend-only repos: omit.) to verify how an existing surface behaves."
- For mobile / backend-only: omit.]

DESIGN DOC:

<PASTE FULL DESIGN DOC FROM STEP 1 HERE>

Output: numbered list of gaps, with file:line citations where applicable. End with `design ready` ONLY if you have zero gaps. Otherwise list them and end with `design needs revision`.
<<<DESIGN_END>>>
```

### Pass C — Readiness (every round)

`description: "Goldfish implementation readiness"`. Stricter than the critic: not "is the design good?" but "is the design _executable_ in one pass?"

```
<<<READINESS_START>>>
You are a fresh implementer with no prior context. Below is a design doc for a feature in the this repo (project name and stack derived from CLAUDE.md / README / manifests) repo. Imagine you've been told: "Implement this. First pass. No follow-up questions allowed." Could you?

For every interface, file path, function signature, API request/response shape, DB column, queue argument, component prop, message type, and verification criterion the doc claims, ask:
- Could I write the corresponding code without asking the author anything?
- Could I verify it works without asking what "works" means?
- Are the cited files and line numbers concrete enough that I'd open the right file and edit the right region?

Output a numbered list of EVERY question you would have to ask the author before you could ship. For each:
- The question itself, one sentence.
- The section of the doc that should have answered it but didn't.

If the list is empty, say "No open questions."

End with EXACTLY one of these closing lines, on its own line:
- implementation ready       (zero open questions; first-pass implementable)
- implementation not ready   (one or more open questions remain)

A design can be beautiful and still fail this gate. The critic asks "is the design good?"; you ask "is the design executable?".

DESIGN DOC:

<PASTE FULL DESIGN DOC FROM STEP 1 HERE>
<<<READINESS_END>>>
```

### Triage and loop

A round is **ready** iff Pass B closes with `design ready` AND Pass C closes with `implementation ready`. Comprehension is informational: log it, surface it to the user, but do not gate progress on it. If comprehension returns `comprehension unclear` AND the round is otherwise ready, still proceed — but flag in the final report that the doc was unclear in places.

If a round is **not ready**, bundle the critic gaps and readiness open questions into a single revise prompt:

```
=== CRITIC GAPS ===
<verbatim Pass B output>

=== READINESS OPEN QUESTIONS ===
<verbatim Pass C output>
```

Plus, if Pass A returned `comprehension unclear`, prepend:

```
=== COMPREHENSION FEEDBACK (informational — the cold reader could not paraphrase parts of the doc) ===
<verbatim Pass A output>
```

Tell the elephant to address EVERY numbered gap from BOTH the CRITIC GAPS and READINESS OPEN QUESTIONS sections — do not collapse or skip a section because the numbering restarts. Each gap is either: addressed in a doc revision, or rebutted with a verbatim reason citing CLAUDE.md / the PRD or other source-of-truth doc (loaded earlier) / the user's words from this conversation. Print the revised doc back to the user once both gates close.

Then re-run Pass B and Pass C against the revised doc (skip Pass A — see above). If the round still does not converge after **three revisions**, the feature is under-specified — **stop and ask the user** for more direction rather than burning more rounds.

## Step 3: Implementation plan

Once the design doc is `design ready`, write a short ordered implementation plan in chat:

**Implementation layer ordering.** Sequence work bottom-up so each layer is testable before the next one depends on it. Examples by stack: **Rails** — migrations → models (with unit tests) → CanCanCan abilities → controllers → views → workers → system tests. **Flutter** — models (run `build_runner` after) → Drift schema migration → network layer → service / BLoC → widgets / screens → navigation → tests. **Node + Vite + Workers** — types → worker routes / D1 migrations → engine/DSP if applicable → frontend components leaf-first → routing → tests in parallel with each layer. Pick the order that matches the detected stack; deviate only with reason.

For trivial features (single-component change), skip this step.

## Step 4: Implement

**Pre-flight check before any code edit:** confirm Step 2 closed both Pass B (Critic) AND Pass C (Readiness). If either is still open, the no-code gate from Step 1 still applies — return to Step 2 instead of proceeding.

Follow the plan. After each layer, briefly verify before moving on:

After each layer, briefly verify before moving on. Examples: migration → run it locally and inspect schema; model → unit test passes, no N+1 (Bullet); controller → curl / browser hit, authorization check from a non-owner account; API endpoint → curl with valid auth, inspect JSON; worker → enqueue from a console and check logs; view / widget → navigate / run on simulator, screenshot, read console for warnings.

**For UI work, drive the feature in the browser / simulator before reporting done.** Web → Chrome MCP at the dev URL. Mobile → simulator run + screenshots + device log. Backend-only → curl + structured response inspection.

If the feature touches a multi-tenant or auth-scoped surface, **verify cross-tenant isolation**: log in as a user on a different tenant and confirm they cannot see / modify the new surface. Do this even if the design doc didn't call it out — the test is cheap and the failure mode is severe.

## Step 5: Hand off to `/eg-precommit-review`

Run `/eg-precommit-review`. Pass the feature name as `$ARGUMENTS` so the reviewer focuses there.

## Step 6: Test gate

```sh
Run the project's lint / typecheck / unit / E2E commands sequentially as separate commands (detect from manifests + CI config + CLAUDE.md). Skip tiers that don't apply.
```

All required tiers must pass. For UI features, **also do a final Chrome MCP / simulator (whichever applies) walkthrough** of the golden path AND the most plausible edge case (empty data, error response, unauthenticated user, stack-specific edge case (e.g. cross-tenant attempt for multi-tenant; offline mode for mobile; degraded clock for time-sensitive), very long input). Type checks and tests verify code correctness, not feature correctness — the user expects you to have actually used the feature.

## Step 7: Final report

Print to the user:
- Feature summary (one line)
- Files touched (grouped by layer: layer names appropriate to the stack (e.g. migrations / models / controllers / api / workers / views / tests; or models / network / service / BLoC / widgets / screens / tests))
- Tests added (file:test name each)
- Design-check result (gaps surfaced and how each was resolved)
- `/eg-precommit-review` outcome (rounds, fixes, rebuttals verbatim)
- Test gate status
- Walkthrough summary: what was driven (Chrome MCP for web; simulator for mobile), golden path traversed, edge cases exercised, cross-tenant verification result if applicable.
- Out-of-scope follow-ups noted in the design doc

**STOP.** Do NOT commit; auto mode does not override the project's commit policy. Wait for the user's literal commit instruction. Follow the convention you observe in `git log` (subject style, ticket reference, trailers). Do not add `Co-Authored-By: Claude` unless the user's existing log already uses it.
