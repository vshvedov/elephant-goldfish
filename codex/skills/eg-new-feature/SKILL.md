---
name: "eg-new-feature"
description: Build a new feature with Codex using design doc, goldfish design check, implementation, review, and validation.
---

# EG New Feature Skill

Build a new feature using the elephant/goldfish workflow. Use the user's text around the `$eg-new-feature` skill mention as the feature description. If no description is provided, ask for one.

If the feature description is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number> --json title,body,labels,comments` and seed the design doc from it.

Before designing, check AGENTS.md/CLAUDE.md for project-specific `eg-*` skills or workflow routing notes. If the request clearly belongs to a more specific local workflow, tell the user and switch only if they agree.

## Scope

Restate the request in one or two sentences and ask the user to confirm if the request is ambiguous or high-impact. For a sharp request, proceed after the restatement.

Do a surface-area sanity check based on the current repo: UI, API, database/schema, background job, external integration, generated code, mobile/platform-specific work, or backend-only logic. Stop for confirmation when the request appears high-impact, destructive, cross-tenant/auth-sensitive, or out of phase with documented project priorities.

## Design Doc

Print a design doc before coding. For substantial features, infer a project-appropriate docs path from AGENTS.md/CLAUDE.md or `docs/`, then ask before saving it.

```text
DESIGN DOC
- Why: <user problem this solves>
- Scope: <in scope and explicitly out>
- Surfaces touched: <files, routes, models, components, jobs, external services>
- Interfaces: <props, signatures, API shapes, DB columns, event payloads>
- UX flow: <click-by-click for UI or request-by-request for backend>
- Project-specific constraints: <auth/scoping, lifecycle, generated code, platform, performance, or other constraints discovered from the repo>
- Failure modes: <what breaks and what the user/API sees>
- Verification criteria: <unit tests, integration/E2E, manual Browser Use/simulator steps>
- Out-of-scope follow-ups: <noted, not built>
```

For UI work, sketch the structure in plain text or pseudo-JSX. If a visual reference is needed, ask for the existing component or screen to mirror.

## Goldfish Design Check

The user invoked this skill, so a fresh design-check subagent is explicitly authorized.

Spawn a fresh Codex subagent with `fork_context: false` and `agent_type: "default"`. If `spawn_agent` is unavailable, run the check locally as a separate cold prompt and keep implementation context out of the prompt.

Send only:

```text
You are a fresh reviewer with no prior context. Below is a design doc for a feature in this repo. AGENTS.md and CLAUDE.md may contain project rules.

Read the design doc and the surfaces it claims to touch. Find holes before implementation starts:
- Is the scope crisp?
- Are interfaces concrete enough that two implementers would converge?
- Do verification criteria actually verify the feature?
- Does the doc misunderstand existing code?
- Are failure modes missing?
- Project-specific constraints: auth/scoping, migrations/backfills, generated code, platform lifecycle, browser/device validation, performance budgets, or other repo-specific risks visible in AGENTS.md/CLAUDE.md and the touched surfaces.
- Are there project-specific gotchas the doc ignores?

For UI work, use Browser Use / in-app browser or a simulator only if the project has a runnable surface and the check would clarify existing behavior.

DESIGN DOC:
<PASTE FULL DESIGN DOC>

Output numbered gaps with file:line citations where applicable. End with `design ready` only if there are zero gaps. Otherwise end with `design needs revision`.
```

Address each real gap in a revised doc, or rebut it with a verbatim reason citing AGENTS.md, CLAUDE.md, a PRD/source-of-truth doc, or the user's words.

If the goldfish flags real gaps three times in a row, stop and ask the user for more direction.

## Implementation

Once the design is `design ready`, write a short ordered implementation plan.

Derive layer ordering from the stack and repo conventions. Typical order: data/schema first, domain/model logic, service/API boundaries, UI/components, navigation/routing, generated code, then tests and manual validation. Keep the plan short for trivial changes.

Implement in that order. After each layer, run a focused verification before moving on.

After each layer, run the narrowest useful verification: focused unit tests, typecheck/analyze, route/API smoke checks, generated-code validation, browser/simulator walkthroughs, or logs.

For UI changes, drive the feature in the browser or simulator before reporting it done. For backend-only changes, use focused tests, curl/API checks, logs, or equivalent runtime verification.

## Review

Use `$eg-precommit-review <feature name>` or apply the same review procedure from the `eg-precommit-review` skill.

## Test Gate

Run:

```sh
<derive from AGENTS.md, CLAUDE.md, package manifests, and CI config>
```

All required tiers must pass. For UI features, do a final Browser Use / in-app browser or simulator walkthrough of the golden path and one plausible edge case.

## Final Report

Report:

- Feature summary
- Files touched by layer
- Tests added
- Design-check result and gap resolutions
- Review outcome, including verbatim rebuttals
- Test gate status
- Manual walkthrough summary
- Out-of-scope follow-ups

Stop short of staging or committing. Follow the commit policy documented in AGENTS.md/CLAUDE.md if the user later asks to commit.
