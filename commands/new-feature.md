---
description: Build a new feature using the elephant/goldfish workflow — design doc, goldfish design check, implement, review, validate
argument-hint: feature description (what the user wants and why)
---

Build a new feature using the elephant/goldfish workflow. The aim: design before code, let a fresh goldfish stress-test the design doc, then implement, review, and validate.

`$ARGUMENTS` is the feature description provided by the user. If empty, ask for one before doing anything. If `$ARGUMENTS` is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number> --json title,body,labels,comments` and seed the design doc from it.

[BOOTSTRAP: project-specific routing note — include if there is a stack-specific verb like `/new-plugin` or `/new-migration`. Example pattern:
"**Routing:** if the request is 'add a new <project-specific artifact>' or anything that needs a new entry in `<project-specific registry>`, use `/<project-specific-command>` instead. This command covers everything else."
Otherwise omit.]

## Step 0: Confirm scope before designing

Restate the request back to the user in 1-2 sentences ("I read this as: <X>. Confirm or correct."). Misreads at this stage waste the most time later. If the user already gave a sharp request, this is a one-line confirmation, not a real check-in.

[BOOTSTRAP: project-priority sanity-check block — include if CLAUDE.md documents priorities or phases. Example pattern:
"Per CLAUDE.md 'Priorities':
- <current-phase priority surface>: green light.
- <stabilization surface>: green light.
- <out-of-phase surface>: **stop and confirm with the user** — energy is supposed to be on <current focus> right now.
- <future-phase surface>: **stop and confirm** — architectural readiness only, not user-facing."
Otherwise omit.]

[BOOTSTRAP: surface-area sanity-check — substitute with stack-relevant categories. Examples:
- Rails: "Pure web/admin UI change: straightforward. API change: versioned API — additive changes are safe, breaking changes need confirm-with-user. POS integration touchpoint: external system, verify the integration's contract before designing. New Sidekiq worker: confirm queue / retry policy / idempotency. Schema change: new migration."
- Flutter: "New screen: check existing patterns under `lib/screens/`. New BLoC: confirm provider scope and stream lifecycle. Network change: backend coordination — does the API endpoint exist? Schema change: `schemaVersion` bump + migration. Platform-specific work: iOS / Android / macOS divergence."
- Generic backend: "Pure logic change: straightforward. API change: backwards-compatibility check. Schema change: migration + backfill. New background job: idempotency + retry policy."]

## Step 1: Write the design doc

Print the design doc to the user. For most features this lives in chat; for substantial features (new domain area, new API resource family, new subsystem) propose writing it to `[BOOTSTRAP: docs path, e.g. `docs/`, `doc/`]` and ask the user before creating the file.

Required sections:

```
DESIGN DOC
- Why: <user problem this solves; cite GH issue, conversation, or PRD section>
- Scope: <what is in; what is explicitly out>
- Surfaces touched: <files / routes / models / controllers / components / DB tables / external services>
- Interfaces: <component props, function signatures, API request/response shapes, DB columns, queue arguments>
- UX flow: <click-by-click for UI; request-by-request for backend>
[BOOTSTRAP: stack-specific design-doc fields — append as needed:
- Rails / multi-tenant: "- Multi-tenant scoping: how this is scoped to current_company / current_user; how cross-tenant access is prevented"
- Rails: "- Authorization: CanCanCan abilities required; new ability rules; admin-only?"
- Flutter: "- State management: which BLoC owns this state; how is it disposed; broadcast vs single-listener; provider scope"
- Flutter: "- Platform considerations: iOS / Android / macOS differences if any"
- Real-time / DSP: "- Allocation budget; lock-free invariants; sample-rate assumptions"]
- Failure modes: <what the user sees when each thing breaks; what the API returns>
- Verification criteria: <unit tests, E2E spec, [BOOTSTRAP: project-specific test artifacts], manual [BOOTSTRAP: Chrome MCP / simulator] steps>
- Out-of-scope follow-ups: <noted, not built>
```

[BOOTSTRAP: PRD reference note — include if the project has a PRD-driven discipline. Example pattern:
"For <PRD-driven surface> work, **reference PRD section numbers** ('implements PRD §6.2') so the doc and the source of truth stay aligned."]

For UI work, sketch the visual structure in plain text or pseudo-JSX. If the design needs a real visual reference, ask the user to point at an existing component to mirror.

## Step 2: Goldfish design check

Spawn a fresh agent:
- `subagent_type: "general-purpose"`
- `description: "Goldfish design check"`

The goldfish gets ONLY the design doc (no chat history, no implementation intent). Its job is to find holes in the doc — not to implement.

**Prompt body to send (between markers, exclusive):**

```
<<<DESIGN_START>>>
You are a fresh reviewer with no prior context. Below is a design doc for a feature in the [BOOTSTRAP: project name + one-sentence description] repo (CLAUDE.md at the repo root has the architecture[BOOTSTRAP: + key concerns to mention, e.g. "including the V3 Grape API, the POS integration layer, and Sidekiq workers" / "including the BLoC + RxDart pattern, ServiceProvider DI, and the Drift-backed cache"]).

Your job: read the design doc, then read the surfaces it claims to touch, and find holes BEFORE implementation starts. Specifically:

- Is the scope crisp? What questions would you have to answer to implement this that the doc does not answer?
- Are the interfaces concrete enough that two implementers would converge on the same result?
- Do the verification criteria actually verify the feature, or only verify that "something rendered"?
- Does the doc misunderstand any existing code? Look up the surfaces it claims to touch and check.
- Are there failure modes the doc missed? Network errors, unauthenticated users, empty state, partial saves, stale data, retries.
[BOOTSTRAP: stack-specific gap items — append, e.g.:
- Rails: "Multi-tenancy: is every read/write properly scoped by tenant? Authorization: are CanCanCan abilities listed? Migration: backfill plan, NOT NULL safety? Versioned API: would this break existing mobile clients?"
- Flutter: "Lifecycle: does every stream/controller have a dispose path? State management: are streams broadcast where multiple listeners exist? Drift: schemaVersion bump if applicable? Backend coordination: does the design assume an endpoint that doesn't exist?"
- Real-time / DSP: "Engine invariants: does the DSP plan allocate in process()? Does it respect the IO/param limits?"]
- Are there project-specific gotchas the doc ignores? CLAUDE.md is your reference.

[BOOTSTRAP: PRD note — include if applicable, e.g. "For <PRD-driven surface> work, also load `<docs/your-prd.md>` and check that the doc is consistent with it."]

[BOOTSTRAP: browser validation note for the goldfish — substitute or remove:
- For web: "For UI work, you may navigate the running dev server via Chrome MCP (`mcp__Claude_in_Chrome__*` against [BOOTSTRAP: dev URL]) to verify how an existing surface behaves."
- For mobile / backend-only: omit.]

DESIGN DOC:

<PASTE FULL DESIGN DOC FROM STEP 1 HERE>

Output: numbered list of gaps, with file:line citations where applicable. End with `design ready` ONLY if you have zero gaps. Otherwise list them and end with `design needs revision`.
<<<DESIGN_END>>>
```

**Triage the gaps.** Each gap is either: addressed in a doc revision, or rebutted with a verbatim reason citing CLAUDE.md / [BOOTSTRAP: PRD or other source-of-truth doc] / the user's words from this conversation. Print the revised doc back to the user once gaps are closed.

If the goldfish flags real gaps three times in a row, the feature is under-specified — **stop and ask the user** for more direction rather than burning more rounds.

## Step 3: Implementation plan

Once the design doc is `design ready`, write a short ordered implementation plan in chat:

[BOOTSTRAP: implementation layer ordering for this stack. Examples:
- Rails: "1. Migrations first. 2. Model changes (associations, validations, scopes, callbacks) + unit tests. 3. CanCanCan ability rules. 4. Service objects / lib classes. 5. Controllers + routes (scoped by current_company). 6. API V3 endpoints + serializers if applicable. 7. Views + partials. 8. JS / page-level scripts. 9. Sidekiq workers + scheduled job registration. 10. System tests + Playwright E2E."
- Vite + Solid + Workers: "1. Backend / data model first (worker routes, D1 migrations, R2 wiring, types). 2. Engine/DSP/graph if applicable. 3. Frontend components in dependency order (leaf controls before composites). 4. Routing and navigation hookup last. 5. Tests in parallel."
- Flutter: "1. Models with JSON serialization (run build_runner after). 2. Drift schema migration if applicable (schemaVersion bump). 3. Network layer + cache hooks. 4. Service / BLoC layer. 5. Widgets / screens (leaf first). 6. Navigation hookup. 7. Tests in parallel."]

For trivial features (single-component change), skip this step.

## Step 4: Implement

Follow the plan. After each layer, briefly verify before moving on:

[BOOTSTRAP: per-layer verification examples for this stack. Examples:
- Rails: "Migration: run + inspect schema. Model: unit test + N+1 check via Bullet. Controller: hit via curl, verify auth via Chrome MCP. API V3: curl with Authorization token, inspect JSON. Worker: enqueue from Rails console. View: Chrome MCP screenshot + console check."
- Vite + Solid: "Backend: hit the route via curl or worker logs. DSP/engine: unit test + tap-in patch reading. Frontend: navigate via Chrome MCP, screenshot, console check."
- Flutter: "Models: flutter analyze clean + .g.dart matches. Service / BLoC: unit test + dispose check. Widget: widget test, no setState-after-dispose. Screen: simulator run + flutter logs."]

[BOOTSTRAP: UI driving rule — pick one:
- For web: "**For UI changes, drive the feature in the browser before reporting it done.** Use Chrome MCP, not the built-in preview tools."
- For mobile: "**For UI features, drive the feature in a real run before reporting it done.** Pick at least one platform (the most common target the user runs on). For features that need cross-platform verification, run on each."
- For backend-only: omit.]

[BOOTSTRAP: cross-tenant or other always-verify reminder if applicable, e.g. "Multi-tenant verification: log in as a user on a different company and confirm they cannot see/modify the new surface."]

## Step 5: Hand off to `/precommit-review`

Run `/precommit-review`. Pass the feature name as `$ARGUMENTS` so the reviewer focuses there.

## Step 6: Test gate

```sh
[BOOTSTRAP: test gate commands per stack — same as fix-bug.md.]
```

All required tiers must pass. For UI features, **also do a final [BOOTSTRAP: Chrome MCP / simulator] walkthrough** of the golden path AND the most plausible edge case (empty data, error response, unauthenticated user, [BOOTSTRAP: stack-specific edge case], very long input). Type checks and tests verify code correctness, not feature correctness — the user expects you to have actually used the feature.

## Step 7: Final report

Print to the user:
- Feature summary (one line)
- Files touched (grouped by layer: [BOOTSTRAP: layer names per stack])
- Tests added (file:test name each)
- Design-check result (gaps surfaced and how each was resolved)
- `/precommit-review` outcome (rounds, fixes, rebuttals verbatim)
- Test gate status
- [BOOTSTRAP: walkthrough field, e.g. "Chrome MCP walkthrough summary (golden path + which edge cases were exercised; cross-tenant verification result)" / "Simulator walkthrough summary (which platform, golden path + failure modes exercised)"]
- Out-of-scope follow-ups noted in the design doc

**STOP.** Do NOT commit; auto mode does not override the project's commit policy. Wait for the user's literal commit instruction. [BOOTSTRAP: commit-policy reminder per project.]
