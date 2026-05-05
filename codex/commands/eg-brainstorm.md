---
description: Generate divergent concept ideas with parallel Codex goldfish and structured synthesis.
---

# EG Brainstorm

Brainstorm a new concept using the elephant/goldfish workflow inverted: multiple fresh goldfish generate divergent ideas, then the elephant synthesizes.

`$ARGUMENTS` is the rough idea. If empty, ask for one.

## Frame

Use Codex structured user input when available. Otherwise ask concise chat questions.

Ask:

1. Stage: raw concept, hypothesis to validate, picking between options, or feature ideation for existing product.
2. Breadth: about 5 deeper concepts, about 10 balanced concepts, or about 20 shallow concepts.
3. Web research: broad, focused prior-art/market context, or off.

## Seed

Print:

```text
SEED
- The thought: <one sentence from $ARGUMENTS>
- What I think the user is really asking: <underlying need>
- Stage: <answer>
- Breadth target: <answer>
- Web research: <answer>
- Constraints inferred: <bullets>
- Success looks like: <one sentence>
- Out of scope: <bullets>
```

Ask whether the seed is right. If not, ask which field needs correction and revise before spawning goldfish.

## Parallel Goldfish

The user invoked this command, so parallel fresh subagents are explicitly authorized.

Pick 3-5 lenses:

- Technical / architectural
- Business / market
- User experience
- Contrarian / pre-mortem
- Market research / prior art
- Adjacent / lateral
- First principles

Spawn each as a fresh Codex subagent with `fork_context: false` and `agent_type: "default"`. If web research is enabled, tell the goldfish to browse/search and cite sources. If a source requires logged-in browser access, the goldfish must ask the elephant to request user approval before navigating.

Each goldfish gets only:

```text
You are a fresh creative thinker with no prior context. Your lens is <LENS NAME>. Stay in that lens.

SEED:
<PASTE SEED>

Generate <PER-LENS COUNT> distinct concepts. For each:
- Name
- The bet
- Why it could win
- Why it could fail
- Sources, if research was used

End with `lens complete`.
```

For breadth targets of 10 or 20, optionally run one more goldfish: "what they all missed."

## Synthesis

Produce:

```text
CONCEPTS BRIEF
Seed: <one-line restatement>

CLUSTERS
<3-5 natural clusters>

RANKED PICKS
1. <concept> — <reasoning and next validation step>
2. <concept> — <reasoning>
3. <concept> — <reasoning>

WHAT THE GOLDFISH AGREED ON
- <signals>

WHAT THEY DISAGREED ON
- <divergences>

OPEN QUESTIONS FOR THE USER
- <questions>
```

## Converge

Ask the user whether to:

- Pick a direction
- Run another round with tighter framing
- Run another round with different lenses
- Save the brief and stop
- Drop it

If saving, write to `[BOOTSTRAP: brainstorm save path]` only after user confirmation.

## Final Report

Report:

- Seed
- Goldfish count and lenses
- Concept count after deduping
- Top 3 picks
- Save path, if any
- Next action

No code changes or commits unless the user explicitly asks for a saved brief.
