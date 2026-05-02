---
description: Generate divergent concept ideas for a raw thought using parallel goldfish, web research, and structured synthesis
argument-hint: rough idea, problem space, or strategic question
---

Brainstorm a new concept using the elephant/goldfish workflow, **inverted**: instead of one goldfish stress-testing the elephant's plan, you spawn **multiple** goldfish in parallel, each with a different lens, each free to be creative and pull from the web. Their lack of shared context with the elephant is the point — they generate divergent ideas, not convergent ones. The elephant then synthesizes.

Use this for **early-stage** thinking: a half-formed app idea, an "I wonder if X" question, a feature whose problem is clear but whose shape isn't, a strategy you're stress-testing before committing. Not for implementation work — for that, hand off to `/new-feature` at the end.

`$ARGUMENTS` is the rough idea. If empty, ask for one before doing anything.

## Step 0: Frame via `AskUserQuestion`

**Every question to the user in this flow goes through `AskUserQuestion`.** No free-form chat questions during framing — structured choices keep the session moving. Free-form refinement is reserved for after the seed is drafted (Step 1).

Ask three questions in sequence (one `AskUserQuestion` call each):

**Q1 — Stage:**
- `question`: "What stage is this at?"
- `header`: `"Stage"`
- `multiSelect`: `false`
- `options`:
  1. **Raw concept** — "I have a vague thought. Cast a wide net, prioritize divergent ideas over depth."
  2. **Hypothesis to validate** — "I have a candidate direction. Stress-test it and surface adjacent options I'm missing."
  3. **Picking between options** — "I have 2-3 directions in mind. Compare, find a fourth, recommend."
  4. **Feature ideation for existing product** — "The product exists. I'm sourcing ideas for what to build next."

**Q2 — Breadth and depth:**
- `question`: "How many concepts should the goldfish surface, total?"
- `header`: `"Breadth"`
- `multiSelect`: `false`
- `options`:
  1. **~5 concepts, deeper** — "Fewer ideas, each more developed. Good when stage is 'hypothesis' or 'picking between'."
  2. **~10 concepts, balanced** — "Default. Mix of depth and breadth."
  3. **~20 concepts, shallow** — "Maximum divergence. Good when stage is 'raw concept' and you want surprises."

**Q3 — Web research:**
- `question`: "Should the goldfish search the web for prior art, comparable products, sources?"
- `header`: `"Web"`
- `multiSelect`: `false`
- `options`:
  1. **On, broad** — "Search freely. Include sources in the brief."
  2. **On, focused** — "Search only for prior art / comparable products / market context. Don't go off on tangents."
  3. **Off** — "First-principles only. No web search. Useful for purely creative or speculative work."

Cache the three answers. They drive the goldfish prompts and the synthesis step.

## Step 1: Draft the seed

Now the elephant writes a **seed**: a tight problem statement that every goldfish will receive. Format:

```
SEED
- The thought: <one sentence verbatim from $ARGUMENTS, lightly cleaned>
- What I think the user is really asking: <one sentence — name the underlying need>
- Stage: <from Q1>
- Breadth target: <from Q2, e.g. "~10 concepts">
- Web research: <from Q3>
- Constraints (inferred — please correct in chat if wrong): <bullet list — likely audience, plausible budget/timeline, tech inclinations, anything else inferable from $ARGUMENTS or the existing repo>
- Success looks like: <one sentence — the elephant's best guess at what a great brief would unlock for the user>
- Out of scope: <bullets — things explicitly NOT being asked here>
```

Print the seed. Then ask via `AskUserQuestion`:

**Q4 — Seed approval:**
- `question`: "Does this seed match what you wanted?"
- `header`: `"Seed?"`
- `multiSelect`: `false`
- `options`:
  1. **Looks right, proceed** — "Spawn the goldfish."
  2. **Refine in chat first** — "I want to correct one or two things in chat before you spawn."
  3. **Restart** — "The seed misread the question. Re-run framing."

If the user picks "Refine in chat first," ask **Q4.5** via `AskUserQuestion` first, to scope the correction (avoid an open-ended "what should I change?"):

**Q4.5 — Which seed field needs correction:**
- `question`: "Which part of the seed needs fixing?"
- `header`: `"Refine"`
- `multiSelect`: `true`
- `options`:
  1. **The thought itself** — "The one-sentence restatement of the user's input is off."
  2. **What I'm really asking** — "The underlying need was misread."
  3. **Constraints** — "The inferred audience / budget / tech assumptions are wrong."
  4. **Success criteria** — "What 'good' looks like is off."
  5. **Out of scope** — "Add or remove items from the out-of-scope list."

Then ask in chat for the correction text for the selected field(s) only — one targeted prompt referencing the chosen fields, not an open-ended "what would you like to change?". Re-print the revised seed and re-ask Q4. If "Restart," go back to Step 0.

## Step 2: Spawn parallel divergent goldfish

Pick **3-5 lenses** based on the seed. Each lens becomes one goldfish. They run in parallel — **send a single message with multiple `Agent` tool uses**, not sequential calls.

Default lens kit (mix and match per the seed):

- **Technical / architectural** — "How could this be built? What stack, what data model, what infrastructure? What's the cheapest viable v0? What tech choice dramatically changes the shape?"
- **Business / market** — "Who pays? What's the model? What's the moat? What does the unit economics look like? What price would clear the market?"
- **User experience** — "Who is the user? What's the moment they reach for this? What's the click-by-click? What's the emotional payoff that brings them back?"
- **Contrarian / pre-mortem** — "Why won't this work? Where does it fail? Who has tried this and bounced off it? What's the boring reason most people won't adopt?"
- **Market research / prior art** — (requires web research enabled) "What already exists? Who are the closest 3-5 competitors? Where is the gap they all leave open? What would 'beat the market' actually mean here?"
- **Adjacent / lateral** — "What's the same problem in a totally different domain? What pattern from a different industry maps onto this? What if we removed the most obvious assumption?"
- **First-principles** — "Strip the problem to its core. What's the minimal artifact that would deliver the value? What is the user actually buying when they buy this?"

Each goldfish gets:
- `subagent_type: "general-purpose"` (full tool access including `WebSearch` if Q3 enabled it)
- `description: "Brainstorm goldfish — <lens name>"`

**Prompt body to send to each goldfish (between markers, exclusive):**

```
<<<BRAINSTORM_START>>>
You are a fresh creative thinker with NO prior context. The user is brainstorming a concept and wants divergent ideas — not a single safe answer. Your lens for this round is: **<LENS NAME>**. Stay in that lens; other goldfish are covering the others.

SEED:
<PASTE FULL SEED FROM STEP 1>

Your job:
1. Generate <PER-LENS COUNT, derived from breadth target ÷ number of lenses, minimum 2> distinct concepts under your lens. Distinct = they would lead to materially different products or strategies, not variations on the same idea.
2. Be creative. Out-of-the-box is good. Surprising is good. Half-formed is fine — capture the spark, not a polished pitch.
3. <IF Q3 = "On, broad" or "On, focused">: Search the web where it sharpens an idea: prior art, comparable products, surprising data points, expert perspectives. Cite sources inline (URL or author).
4. For each concept, give:
   - **Name** (3-6 words, evocative)
   - **The bet** (1-2 sentences — what's the core idea, why is it interesting)
   - **Why it could win** (1 sentence)
   - **Why it could fail** (1 sentence — be honest)
   - **Sources** (URLs / refs if web research used)

Do NOT propose to "combine" with other lenses or "cover all the bases." Push the lens hard. Synthesis happens later, by someone else.

End with the literal string `lens complete`.
<<<BRAINSTORM_END>>>
```

Substitute `<LENS NAME>`, `<PASTE FULL SEED FROM STEP 1>`, `<PER-LENS COUNT>`, and the conditional web-research line per goldfish.

## Step 3: Optional contrarian sweep

After all parallel goldfish return, if and only if the breadth target was "~10" or "~20," spawn ONE more goldfish:

- `subagent_type: "general-purpose"`
- `description: "Brainstorm goldfish — what they all missed"`

This one gets the seed PLUS the deduplicated set of all concepts so far, and is asked: "What did they ALL miss? What lens didn't anyone use? What concept would a smart outsider propose that none of these touch?" Output 2-3 additional concepts in the same format.

## Step 4: Synthesize the concepts brief

Now the elephant. Read every goldfish's output. Produce the **concepts brief**:

```
CONCEPTS BRIEF
Seed: <one-line restatement>

CLUSTERS
<group concepts by theme — usually 3-5 clusters emerge naturally>

<For each cluster:>
  ## <Cluster name>
  - <Concept name>: <the bet, 1 sentence> [lens: <which goldfish>] <[sources: URL, URL] if any>
  - <Concept name>: ...

RANKED PICKS (elephant's view, with reasoning)
1. **<Concept name>** — <why this ranks first; what evidence in the brief supports it; what's the next step to validate>
2. **<Concept name>** — ...
3. **<Concept name>** — ...

WHAT THE GOLDFISH AGREED ON
- <2-3 bullets — convergent signals across lenses are usually load-bearing>

WHAT THEY DISAGREED ON
- <2-3 bullets — divergence is where the interesting questions live>

OPEN QUESTIONS FOR THE USER
- <bullet list of things only the user can answer: priorities, constraints, taste>
```

Print the full brief. Cite sources inline where they exist.

## Step 5: Converge via `AskUserQuestion`

After the brief, ask:

**Q5 — Next move:**
- `question`: "What's the next move?"
- `header`: `"Converge"`
- `multiSelect`: `false`
- `options`:
  1. **Pick a direction** — "I want to commit to one of the ranked picks (or one I'll name)."
  2. **Another round, tighter framing** — "Re-run with a sharper seed (I'll refine constraints in chat)."
  3. **Another round, different lenses** — "Re-run with different goldfish lenses (I'll pick)."
  4. **Save brief and stop** — "Good output, file it for later, no immediate action."
  5. **Drop it** — "This direction isn't worth pursuing."

If **Pick a direction**: ask **Q6** via `AskUserQuestion`. Use the **top 3 ranked picks** from the brief as the first three options, plus two escape hatches. Do NOT ask "which concept?" in free-form chat — the concepts are enumerable, so they belong as options.

**Q6 — Which concept to commit to:**
- `question`: "Which concept do you want to commit to?"
- `header`: `"Concept"`
- `multiSelect`: `false`
- `options`:
  1. **<Top ranked pick name>** — "<one-line bet from the brief>"
  2. **<2nd ranked pick name>** — "<one-line bet from the brief>"
  3. **<3rd ranked pick name>** — "<one-line bet from the brief>"
  4. **A different concept from the brief** — "I'll name one of the others in chat."
  5. **A hybrid or new direction** — "I'll describe a combination or fresh angle in chat."

If the user picks options 4 or 5, ask in chat with one targeted prompt: option 4 → "Which concept from the brief?"; option 5 → "Describe the hybrid or new direction in one or two sentences." Both are inherently free-form; everything else is a click.

Then ask **Q7** via `AskUserQuestion`:

**Q7 — Handoff:**
- `question`: "Want to spin the chosen concept into `/new-feature` to start designing the build?"
- `header`: `"Handoff"`
- `multiSelect`: `false`
- `options`:
  1. **Yes, hand off to `/new-feature`** — "Use the chosen concept as the feature description."
  2. **Not yet** — "I'll sit with it. Save the brief and stop."

If they pick yes, end this command and tell the user: "Run `/new-feature <chosen concept name + one-sentence description>` when ready."

If **Another round, tighter framing**: capture the user's refinements in chat, update the seed, re-run from Step 2 with the same lenses.

If **Another round, different lenses**: present the lens kit (Step 2's list) via `AskUserQuestion` with `multiSelect: true` and let the user pick. Re-run from Step 2 with the new selection.

If **Save brief and stop**: write the concepts brief to `[BOOTSTRAP: docs path or inferred working-notes location, e.g. `docs/brainstorms/<slug>-<YYYY-MM-DD>.md` or `notes/`]` ONLY if the user confirms via one more `AskUserQuestion`:

**Q8 — Save location:**
- `question`: "Where should I save the brief?"
- `header`: `"Save"`
- `multiSelect`: `false`
- `options`:
  1. **<inferred path>** — "Save to <path>."
  2. **Just print, don't save** — "Keep it in chat only."
  3. **Different path** — "I'll specify in chat."

If **Drop it**: print one-line acknowledgement and stop.

## Final report

Print to the user:
- Seed (one line)
- Number of goldfish run, with lenses
- Number of concepts surfaced (post-dedup)
- Top 3 ranked picks with one-line reasoning each
- Where the brief was saved (if anywhere)
- Next action (handoff to `/new-feature`, refinement, or stop)

**STOP.** No commit, no code changes — this command produces a brief, not a diff. If the user picked the handoff option, they'll invoke `/new-feature` themselves on the next turn.
