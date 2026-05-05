---
name: "eg-new-feature"
description: Build a new feature with Codex using design doc, goldfish design check, implementation, review, and validation.
---

# EG New Feature Skill

Build a new feature using the elephant/goldfish workflow. Use the user's text around the `$eg-new-feature` skill mention as the feature description. If no description is provided, ask for one.

If the feature description is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number> --json title,body,labels,comments` and seed the design doc from it.

[BOOTSTRAP: project-specific routing note]

## Scope

Restate the request in one or two sentences and ask the user to confirm if the request is ambiguous or high-impact. For a sharp request, proceed after the restatement.

[BOOTSTRAP: surface-area sanity-check]

## Design Doc

Print a design doc before coding. For substantial features, ask before saving it to `[BOOTSTRAP: docs path]`.

```text
DESIGN DOC
- Why: <user problem this solves>
- Scope: <in scope and explicitly out>
- Surfaces touched: <files, routes, models, components, jobs, external services>
- Interfaces: <props, signatures, API shapes, DB columns, event payloads>
- UX flow: <click-by-click for UI or request-by-request for backend>
[BOOTSTRAP: stack-specific design-doc fields]
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
You are a fresh reviewer with no prior context. Below is a design doc for a feature in the [BOOTSTRAP: project name + one-sentence description] repo. AGENTS.md and CLAUDE.md may contain project rules.

Read the design doc and the surfaces it claims to touch. Find holes before implementation starts:
- Is the scope crisp?
- Are interfaces concrete enough that two implementers would converge?
- Do verification criteria actually verify the feature?
- Does the doc misunderstand existing code?
- Are failure modes missing?
[BOOTSTRAP: stack-specific gap items]
- Are there project-specific gotchas the doc ignores?

[BOOTSTRAP: browser validation note for design check]

DESIGN DOC:
<PASTE FULL DESIGN DOC>

Output numbered gaps with file:line citations where applicable. End with `design ready` only if there are zero gaps. Otherwise end with `design needs revision`.
```

Address each real gap in a revised doc, or rebut it with a verbatim reason citing AGENTS.md, CLAUDE.md, a PRD/source-of-truth doc, or the user's words.

If the goldfish flags real gaps three times in a row, stop and ask the user for more direction.

## Implementation

Once the design is `design ready`, write a short ordered implementation plan.

[BOOTSTRAP: implementation layer ordering]

Implement in that order. After each layer, run a focused verification before moving on.

[BOOTSTRAP: per-layer verification examples]

[BOOTSTRAP: browser validation block]

## Review

Use `$eg-precommit-review <feature name>` or apply the same review procedure from the `eg-precommit-review` skill.

## Test Gate

Run:

```sh
[BOOTSTRAP: test gate commands]
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

Stop short of staging or committing. [BOOTSTRAP: commit policy reminder]
