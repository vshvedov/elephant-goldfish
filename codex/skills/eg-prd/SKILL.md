---
name: "eg-prd"
description: Build a PRD with Codex using codebase grounding, gap-filling, research goldfish, and synthesis.
---

# EG PRD Skill

Build a Product Requirements Document from a rough idea. Use the user's text around the `$eg-prd` skill mention as the seed. If no seed is provided, ask for one.

If the seed is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number>` and use its title and body as the seed.

## Frame

Use Codex structured user input when available. Otherwise ask concise chat questions.

Ask:

1. Depth: lightweight, standard, or comprehensive.
2. Research scope: none, web search only, or web plus Browser Use / in-app browser for gated sources.
3. Output target: save to `[BOOTSTRAP: prd save path]`, print/chat only, hand off to new-feature, save durable nuggets to AGENTS.md.

## Codebase Grounding

The user invoked this skill, so fresh subagents for codebase grounding are explicitly authorized.

Spawn 1-2 fresh Codex subagents with `fork_context: false`; use `agent_type: "explorer"` when available.

- Goldfish A: existing surfaces near the seed. Report file:line citations, data model, routes/endpoints/screens.
- Goldfish B: architecture and conventions. Read AGENTS.md, CLAUDE.md, docs, manifests, and recent commits. Report stack, auth/scoping, testing tiers, deployment topology, and constraints.

The elephant prints:

```text
CODEBASE BRIEF
- Closest existing surfaces:
- Patterns to mirror:
- Constraints from AGENTS.md / CLAUDE.md / docs:
- Observed gaps:
```

## Gap List

Surface gaps grouped by:

- Who and why
- What and scope
- How well
- When
- Constraints
- Failure modes
- Pricing and go-to-market, if relevant
- Instrumentation

Number gaps globally as G1, G2, etc. Ask which gaps to fill before drafting. Unselected gaps go into Open Questions.

For each selected gap, ask a structured question with 3-5 plausible answers plus "defer" and "other".

## Research

If research scope is not "none", spawn 3-5 fresh research goldfish in parallel with `fork_context: false`.

Possible lenses:

- Market and prior art
- Technical patterns
- UX precedent
- Compliance and risk
- Performance and scale

Each goldfish gets only:

```text
You are a fresh researcher with no prior context. Your lens is <LENS NAME>.

SEED: <PASTE USER SEED>
CODEBASE BRIEF: <PASTE>
ANSWERED GAPS: <PASTE>

Research your lens. Produce 5-10 numbered findings with sources, then 3-5 bullets on what this implies for the PRD.

If Browser Use / in-app browser access to a logged-in or sensitive source is needed, stop and tell the elephant what you want to inspect and why.

End with `lens complete`.
```

The elephant summarizes research by lens and consolidates sources.

## PRD

Draft:

```text
# PRD: <title>

## Executive Summary
## Problem Statement
## Target Users
## Current State
## Proposed Solution
## Scope
## User Stories / Jobs To Be Done
## Functional Requirements
## Non-Functional Requirements
## Success Metrics
## Risks & Mitigations
## Implementation Hints
## Open Questions
## Sources & References
## Out-of-Scope Follow-Ups
```

Skip sections only when genuinely not applicable. Mark deferred gaps as Open Questions.

## Review And Output

Ask whether the PRD is approved, needs specific section revisions, should restart, or should stop.

If approved, apply the selected output targets:

- Save PRD to `[BOOTSTRAP: prd save path]` if selected.
- Persist only durable cross-cutting nuggets to AGENTS.md if selected; show the diff before applying.
- Print the exact `Use $eg-new-feature to build <summary>` handoff prompt if selected.

## Final Report

Report:

- PRD title
- Depth and research scope
- Codebase brief summary
- Gaps surfaced, filled, deferred
- Research lenses run
- Output location
- Next action

Stop short of staging or committing. [BOOTSTRAP: commit policy reminder]
