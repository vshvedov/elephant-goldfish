---
name: eg-prd
description: Build a thorough Product Requirements Document from a rough idea. Uses codebase grounding, structured gap-filling, deep research, and parallel goldfish synthesis.
---

Build a Product Requirements Document for an idea or feature, with high rigor: ground the request in the actual codebase, surface every gap in the user's description and resolve them through structured Q&A, then run deep research (web search, parallel goldfish) before synthesizing the PRD. Output is the PRD itself, ready to feed into `eg-new-feature` or be saved as a durable artifact.

If the user gave a GitHub issue URL or `#<number>`, fetch it first with `run_shell_command` using `gh issue view <number>` and use its title + body as the seed.

**Question discipline:** every question to the user in this flow goes through the `ask_user` tool. Free-form chat is reserved for unbounded answers ONLY after an `ask_user` prompt scopes the reason.

## Step 0: Frame the run via `ask_user`

Use a single `ask_user` call with three questions:

**Q1 — Depth:**
- `question`: "How deep should this PRD go?"
- `header`: `"Depth"`
- `multiSelect`: `false`
- `options`:
  1. **Lightweight (1-2 pages)** — "MVP-style PRD: problem, scope, success criteria, open questions. Skips deep research."
  2. **Standard (3-5 pages)** — "Default. Full PRD with codebase grounding, light research, and prioritized gap-filling."
  3. **Comprehensive (5+ pages)** — "Heavy research, multiple goldfish, market+technical+UX+compliance lenses. For high-stakes or unfamiliar domains."

**Q2 — Research scope:**
- `question`: "How much external research should the goldfish do?"
- `header`: `"Research"`
- `multiSelect`: `false`
- `options`:
  1. **None** — "First-principles + codebase only. Useful for internal tooling or speculative work."
  2. **Web search only** — "Public web for prior art, comparable products, technical patterns."

**Q3 — Output target:**
- `question`: "Where should the PRD end up?"
- `header`: `"Output"`
- `multiSelect`: `true`
- `options`:
  1. **Save as `[BOOTSTRAP: prd path, e.g. `docs/prds/<slug>-<YYYY-MM-DD>.md` or `docs/specs/`]`** — "Durable artifact. Recommended for anything Standard or Comprehensive."
  2. **Print and chat only** — "PRD lives in this conversation."
  3. **Hand off to `eg-new-feature` after** — "Suggest invoking `eg-new-feature`."
  4. **Save to memory** — "Persist as a durable note to the project's memory file."

Cache the answers. They drive the rest of the run.

## Step 1: Ground in the codebase

Before asking the user anything else, the elephant must understand the existing codebase well enough to know what's already there. Spawn **1-2 goldfish in parallel** using `invoke_agent` (`agent_name="codebase_investigator"` or `"generalist"`):

- **Goldfish A — "Existing surfaces"**: Find code that already touches the same domain as the seed. Report file:line citations of the closest analogues, the data model, the URL routes.
- **Goldfish B — "Architecture and conventions"**: Read GEMINI.md, the package manifests, recent commits referencing this area. Report constraints.

**Execute the `invoke_agent` tool calls concurrently.**

After both return, the elephant prints a **codebase brief** (5-15 lines):

```
CODEBASE BRIEF
- Closest existing surfaces: <files / routes / models with one-line description each>
- Patterns to mirror: <e.g. "uses Drift schema migrations">
- Constraints from GEMINI.md or recent decisions: <multi-tenant, etc.>
- Observed gaps the seed leaves open: <preview of what Step 2 will turn into questions>
```

## Step 2: Surface every gap

Produce a complete list of gaps. Categories:
- **Who & why**: target user persona, the job-to-be-done
- **What**: in-scope behavior, out-of-scope explicitly, MVP vs. full
- **How well**: success metrics, scale assumptions
- **Constraints**: budget, compliance, multi-tenant scoping
- **Failure modes**: what does the user see when it breaks

Print the gap list grouped by category.

Then ask via `ask_user`:

**Q4 — Gap prioritization:**
- `question`: "Which gaps do you want to fill before drafting? (Unselected gaps land in the PRD's Open Questions section.)"
- `header`: `"Gaps"`
- `multiSelect`: `true`
- `options`: 
  1. **Who & why**
  2. **What & scope**
  3. **How well**
  4. **Constraints**
  5. **All of the above**

## Step 3: Fill the selected gaps

For every gap category the user selected, use `ask_user` to present the specific gaps and 3-5 plausible answers. Use "Other (describe in chat)" or "Defer to PRD's Open Questions" as escape hatches.

If the user picks **Defer**, write that gap into the PRD's Open Questions verbatim.

## Step 4: Deep research (if Q2 was not "None")

Spawn **3-5 research goldfish in parallel** using `invoke_agent` (`agent_name="generalist"`). 

Default lens kit (mix and match):
- **Market & prior art** 
- **Technical patterns** 
- **UX precedent** 
- **Compliance & risk** 
- **Performance & scale** 

**Each goldfish prompt body:**

```
You are a fresh researcher with NO prior context. Your lens for this round is: **<LENS NAME>**. Stay in that lens.

SEED: <PASTE user input verbatim>

CODEBASE BRIEF: <PASTE Step 1 output>

ANSWERED GAPS: <PASTE Step 3 answers>

Your job:
1. Research your lens against the seed + answered gaps. Be specific.
2. Web search (`google_web_search` or `web_fetch`) where it sharpens an answer. Cite URLs inline.
3. Output for your lens: 5-10 numbered findings.
4. End with **What this lens implies for the PRD** — 3-5 bullets the PRD synthesis should reflect.
```

After all goldfish return, the elephant prints a **research summary**.

## Step 5: Synthesize the PRD

Draft the PRD by integrating everything. Use this structure:

```
# PRD: <title>
## Executive summary
## Problem statement
## Target users
## Current state
## Proposed solution
## Scope (In / Out)
## User stories
## Functional requirements
## Non-functional requirements (Performance, Security, etc.)
## Success metrics
## Risks & mitigations
## Implementation hints
## Open questions
## Sources & references
```

Print the full PRD.

## Step 6: User review

Ask via `ask_user`:

**Q-final-1 — PRD verdict:**
- `question`: "What's next for this PRD?"
- `header`: `"Verdict"`
- `multiSelect`: `false`
- `options`:
  1. **Approve as-is** — "Proceed to output (Step 7)."
  2. **Refine specific sections** — "I'll pick which sections to revise."
  3. **Reject and restart**
  4. **Stop here**

If **Refine specific sections**, use `ask_user` to let them pick which ones, then ask for chat input to revise.

## Step 7: Output

Drive the output by what the user picked in Q3.
- **Save as `<path>`**: Use `write_file` to write the PRD to disk. Create the directory via `run_shell_command` with `mkdir -p` if needed.
- **Save to memory**: Write the durable nuggets (not the full body) to the project's memory via `write_file`.
- **Hand off to `eg-new-feature`**: Remind the user they can trigger it.

**STOP.** Do NOT commit. [BOOTSTRAP: commit-policy reminder per project.]