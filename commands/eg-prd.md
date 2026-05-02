---
description: Build a thorough PRD from a rough idea: codebase grounding, structured gap-filling, deep research, parallel goldfish synthesis
argument-hint: idea or feature description (the PRD's seed)
---

Build a Product Requirements Document for an idea or feature, with high rigor: ground the request in the actual codebase, surface every gap in the user's description and resolve them through structured Q&A, then run deep research (web search, parallel goldfish, optional Chrome MCP for logged-in sources) before synthesizing the PRD. Output is the PRD itself, ready to feed into `/eg-new-feature` or be saved as a durable artifact.

This sits **between** `/eg-brainstorm` (concept exploration) and `/eg-new-feature` (implementation): `/eg-brainstorm` asks "what should we build?"; `/eg-prd` asks "what exactly are we building, and what's the surrounding context?"; `/eg-new-feature` asks "how do we ship it?"

`$ARGUMENTS` is the idea. If empty, ask for one before doing anything. If `$ARGUMENTS` is a GitHub issue URL or `#<number>`, fetch it with `gh issue view <number>` and use its title + body as the seed.

**Question discipline:** every question to the user in this flow goes through `AskUserQuestion`. Free-form chat is reserved for the moments where the answer is genuinely unbounded (a custom file path, a verbatim correction string), and even then only AFTER an `AskUserQuestion` has scoped the reason for the chat input.

## Step 0: Frame the run via `AskUserQuestion`

Three questions in sequence (one `AskUserQuestion` call each):

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
  2. **Web search only** — "Public web for prior art, comparable products, technical patterns. No browser sessions."
  3. **Web + Chrome MCP for gated sources** — "Web plus Chrome MCP for Reddit, X, paywalled articles, internal dashboards — anything that needs a logged-in browser. Goldfish will tell you what they need to look up before navigating."

**Q3 — Output target:**
- `question`: "Where should the PRD end up?"
- `header`: `"Output"`
- `multiSelect`: `true`
- `options`:
  1. **Save as `[BOOTSTRAP: prd path, e.g. `docs/prds/<slug>-<YYYY-MM-DD>.md` or `docs/specs/`]`** — "Durable artifact. Recommended for anything Standard or Comprehensive."
  2. **Print and chat only** — "PRD lives in this conversation. Good for Lightweight or throwaway exploration."
  3. **Hand off to `/eg-new-feature` after** — "Once the PRD is approved, end with the literal `/eg-new-feature <one-line summary>` so the next step is one command away."
  4. **Save to memory** — "Persist as a durable note (e.g. CLAUDE.md or your memory system) for future sessions to recall. Prefer this for cross-cutting policies the PRD discovers, not the full doc."

Cache the three answers. They drive the rest of the run.

## Step 1: Ground in the codebase

Before asking the user anything else, the elephant must understand the existing codebase well enough to know what's already there. Spawn **1-2 goldfish in parallel** with `subagent_type: "Explore"` (fall back to `"general-purpose"` if Explore is unavailable):

- **Goldfish A — "Existing surfaces"**: Find code that already touches the same domain as the seed. Report file:line citations of the closest analogues, the data model, the URL routes / API endpoints / screens that are nearby.
- **Goldfish B — "Architecture and conventions"**: Read CLAUDE.md, any `docs/` index, the package manifests, recent commits referencing this area. Report: tech stack, multi-tenancy / auth model, testing tiers, deployment topology, anything that constrains how a new feature would land.

**Send a single message with both `Agent` tool uses** so they run concurrently.

After both return, the elephant prints a **codebase brief** (5-15 lines):

```
CODEBASE BRIEF
- Closest existing surfaces: <files / routes / models with one-line description each>
- Patterns to mirror: <e.g. "uses Drift schema migrations with schemaVersion bump"; "controllers scope by current_company">
- Constraints from CLAUDE.md or recent decisions: <multi-tenant, COEP headers, frozen module set, etc.>
- Observed gaps the seed leaves open: <preview of what Step 2 will turn into questions>
```

## Step 2: Surface every gap

Now the elephant analyzes `$ARGUMENTS` and the codebase brief, and produces a complete list of gaps. Categories to cover (omit only if genuinely n/a):

- **Who & why**: target user persona, the job-to-be-done, the trigger / moment of need
- **What**: in-scope behavior, out-of-scope explicitly, MVP vs. full, feature variants or modes
- **How well**: success metrics (numerical where possible), performance budgets, accessibility level, scale assumptions
- **When**: deadline if any, dependencies on other work, sequencing
- **Constraints**: budget, tech stack restrictions, compliance (GDPR / SOC2 / PCI / industry-specific), brand voice, multi-tenant scoping, internationalization, offline behavior
- **Failure modes**: what does the user see when each thing breaks; rollback plan; degraded modes
- **Pricing & go-to-market** (if a paid feature): tier, packaging, sales motion
- **Instrumentation**: what events / logs / metrics fire; what dashboards exist for it after launch

Print the gap list grouped by category. Number every gap globally (G1, G2, …). Each gap is one line: the question and why it matters.

Then ask via `AskUserQuestion`:

**Q4 — Gap prioritization:**
- `question`: "Which gaps do you want to fill before drafting? (Unselected gaps land in the PRD's Open Questions section.)"
- `header`: `"Gaps"`
- `multiSelect`: `true`
- `options` — produce one option per gap, **but** AskUserQuestion supports a limited number of options (around 5). If there are more gaps than fit, group them: each option represents a category (e.g. "Who & why — 3 gaps", "How well — 4 gaps") and the user picks categories to fill. The default kit:
  1. **Who & why** — "Persona, job-to-be-done, trigger."
  2. **What & scope** — "In/out, MVP, variants."
  3. **How well** — "Metrics, performance, accessibility, scale."
  4. **Constraints** — "Compliance, multi-tenant, tech stack, budget."
  5. **All of the above + failure modes & instrumentation** — "Fill everything detected."

If the gap count is small (≤5) AND each gap is sharp and self-contained, present individual gaps as the options instead of categories. Use judgment.

## Step 3: Fill the selected gaps

For every gap the user selected, ask one `AskUserQuestion` per gap. Each question is structured: present the gap, list 3-5 plausible answers (the elephant's best educated guesses based on the codebase brief and `$ARGUMENTS`), plus an "Other (describe in chat)" escape hatch. Concrete pattern:

```
Q5+ — <Gap label>:
- question: "<the gap, phrased as a question>"
- header: "<short tag>"
- multiSelect: false (or true when genuinely multi-pick, e.g. "Which platforms?")
- options:
  1. <plausible answer 1, with one-line justification>
  2. <plausible answer 2>
  3. <plausible answer 3>
  4. **Defer to PRD's Open Questions** — "I don't know yet; capture as open."
  5. **Other (describe in chat)** — "None of the above; I'll specify."
```

If the user picks **Defer**, write that gap into the PRD's Open Questions section verbatim and move on. If **Other**, ask in chat with one targeted prompt referencing the gap's label, then continue.

Do NOT ask all gaps in one shot. Stream them — the user sees the running picture build up. Skip Step 3 entirely if the user picked nothing in Q4.

## Step 4: Deep research (if Q2 was not "None")

Spawn **3-5 research goldfish in parallel** using `subagent_type: "general-purpose"` (full tool access). Pick lenses based on the seed and the answered gaps. **Send one message with all `Agent` tool uses** so they run concurrently.

Default lens kit (mix and match):

- **Market & prior art** — "What products / open-source projects / past attempts already exist in this space? Top 3-5 closest analogues, what they do well, where they fail, what users complain about."
- **Technical patterns** — "Reference architectures, libraries, frameworks. What's the 'standard' way to build this? What's a controversial-but-better way?"
- **UX precedent** — "Canonical UX for this kind of feature. Specific examples (named products, screenshot descriptions if helpful). What conventions users will expect."
- **Compliance & risk** — "Regulatory exposure, accessibility requirements, security posture, privacy obligations. What MUST this PRD account for?"
- **Performance & scale** — "Realistic numbers for a feature of this kind: latency budgets, concurrency, data volume, cost-per-action. Source the numbers."

**Each goldfish prompt body (between markers, exclusive):**

```
<<<RESEARCH_START>>>
You are a fresh researcher with NO prior context. Your lens for this round is: **<LENS NAME>**. Stay in that lens.

SEED: <PASTE $ARGUMENTS verbatim>

CODEBASE BRIEF: <PASTE Step 1 output>

ANSWERED GAPS: <PASTE Step 3 answers>

Your job:
1. Research your lens against the seed + answered gaps. Be specific — name products, cite numbers, quote sources.
2. Web search where it sharpens an answer. Cite URLs inline.
3. <IF Q2 = "Web + Chrome MCP">: For sources that require a logged-in browser session (Reddit, X / Twitter, paywalled articles, internal dashboards, etc.), use Chrome MCP (`mcp__Claude_in_Chrome__*`) against the user's running browser. Get tab context first via `tabs_context_mcp`, then `navigate` and `get_page_text`. **Before navigating to a site that requires auth or might charge / submit forms, stop and tell the orchestrator what you intend to look at and why.** The orchestrator will surface to the user.
4. Output for your lens: 5-10 numbered findings, each one tight (1-3 sentences), each with at least one source URL or named reference.
5. End with **What this lens implies for the PRD** — 3-5 bullets the PRD synthesis should reflect.

End with the literal string `lens complete`.
<<<RESEARCH_END>>>
```

After all goldfish return, the elephant prints a **research summary** (no synthesis yet — that's Step 5):

- One section per lens, each with the goldfish's findings + implications.
- Sources consolidated at the end.
- Anything the goldfish flagged as "needs human verification" surfaced explicitly.

If a goldfish stopped to ask about a Chrome MCP navigation, surface the question to the user via `AskUserQuestion`:

**Q-N — Research navigation approval:**
- `question`: "Goldfish <lens> wants to navigate to <URL> to look up <topic>. Allow?"
- `header`: `"Browse?"`
- `multiSelect`: `false`
- `options`:
  1. **Yes, navigate** — "Use my browser session to read this page."
  2. **No, skip** — "Proceed without this source."
  3. **Different source** — "I'll suggest a better URL in chat."

## Step 5: Synthesize the PRD

The elephant now drafts the PRD by integrating: `$ARGUMENTS`, the codebase brief, the answered gaps, the unanswered gaps (open questions), the research summary. Use this structure (skip sections that are genuinely n/a; mark sections "TBD" if the gap was deferred to Open Questions):

```
# PRD: <title>

## Executive summary
<2-4 sentences: what, who for, why now>

## Problem statement
<the underlying user / business problem, stated independently of solution>

## Target users
<persona(s), JTBD, trigger / moment of need — from gap answers>

## Current state
<from codebase brief: what exists today, what's adjacent, what we'd reuse vs. replace>

## Proposed solution
<the shape of the answer — high-level, NOT implementation>

## Scope
**In:** <bullets>
**Out:** <bullets — explicitly>

## User stories / Jobs-to-be-done
<as-a / I-want / so-that, or JTBD format>

## Functional requirements
<numbered list, each requirement testable>

## Non-functional requirements
- **Performance:** <budgets>
- **Accessibility:** <level, e.g. WCAG 2.1 AA>
- **Security & privacy:** <auth, data handling, PII>
- **Multi-tenant / scoping:** <if applicable>
- **i18n / localization:** <if applicable>
- **Offline / degraded modes:** <if applicable>

## Success metrics
<numerical where possible, with target values + measurement method>

## Risks & mitigations
<table or bulleted list: risk, likelihood, impact, mitigation>

## Implementation hints
<loose; refined later in /eg-new-feature: layer ordering, data model sketch, key dependencies>

## Open questions
<gaps the user deferred, plus anything research surfaced as needing human verification>

## Sources & references
<all goldfish citations, deduplicated, grouped by theme>

## Out-of-scope follow-ups
<noted, not built; future PRDs>
```

Print the full PRD.

## Step 6: User review

Ask via `AskUserQuestion`:

**Q-final-1 — PRD verdict:**
- `question`: "What's next for this PRD?"
- `header`: `"Verdict"`
- `multiSelect`: `false`
- `options`:
  1. **Approve as-is** — "Proceed to output (Step 7)."
  2. **Refine specific sections** — "I'll pick which sections to revise."
  3. **Reject and restart** — "The PRD missed the mark. Re-run from Step 0."
  4. **Stop here** — "Print only, don't save or hand off."

If **Refine specific sections**, ask:

**Q-refine — Which sections:**
- `question`: "Which sections need revision?"
- `header`: `"Refine"`
- `multiSelect`: `true`
- `options`: one per major PRD section (Executive summary / Problem / Target users / Scope / Functional / Non-functional / Metrics / Risks / Open questions). Add an "Add a section I missed" escape hatch.

For each picked section, ask in chat with one targeted prompt referencing the section's content. Re-draft the affected sections, re-print the PRD, re-ask Q-final-1.

If **Reject and restart**, go back to Step 0.

## Step 7: Output

Drive the output by what the user picked in Q3 (output target). Each Q3 selection produces a side-effect:

- **Save as `<path>`**: write the PRD to disk. If the path includes `<slug>` and `<YYYY-MM-DD>`, derive the slug from the PRD title (kebab-case, lowercase) and date from `date +%Y-%m-%d`. If the directory doesn't exist, create it. Confirm the path back to the user.
- **Save to memory**: write the cross-cutting policies / constraints the PRD discovered (NOT the full PRD body — just the durable nuggets that future sessions should know) to the project's memory system or CLAUDE.md. Surface the diff before applying.
- **Hand off to `/eg-new-feature`**: print the literal command the user can paste to invoke `/eg-new-feature`, with a one-line feature description sourced from the PRD's executive summary. Example: `Run /eg-new-feature implement <PRD title>: <one-line summary> when ready.` Do NOT auto-invoke.
- **Print and chat only**: do nothing further.

If multiple Q3 options were picked, do all of them.

## Final report

Print to the user:
- PRD title (one line)
- Depth + research scope chosen
- Codebase brief one-line summary
- Gaps surfaced / filled / deferred (counts)
- Research lenses run
- Where the PRD lives now (file path, memory entry, both, or chat-only)
- Next action (e.g. "Run `/eg-new-feature ...` when ready" or "Open questions need user input before this is shippable")

**STOP.** Do NOT commit; auto mode does not override the project's commit policy. If the PRD was saved to disk, it's a new file the user will commit themselves when ready. [BOOTSTRAP: commit-policy reminder per project.]
