# Snippet to inject into target GEMINI.md

This is the section that gets added to the target repo's `GEMINI.md` during bootstrap. Tailor the placeholders, then inject. Do not include this header line or the surrounding text — only what's between the `<<<SNIPPET_START>>>` and `<<<SNIPPET_END>>>` markers.

```
<<<SNIPPET_START>>>
## Working with Gemini CLI (Elephant/Goldfish Skills)

This project has installed five [Gemini CLI Skills](https://github.com/google/gemini-cli) in `.gemini/skills/` that wrap an "elephant/goldfish" workflow inspired by [this article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874): the "elephant" is the working session with full context; the "goldfish" is a fresh subagent spawned via `invoke_agent` with no prior context.

For implementation work, the goldfish stress-tests a problem/design doc or a diff. For brainstorming and PRD writing, multiple goldfish run in parallel with different lenses to generate divergent ideas or research findings the elephant synthesizes.

These are activated contextually based on your intent, but you can explicitly trigger them by naming the skill:

| Intent | Skill Trigger | Description |
|---|---|---|
| Early-stage concept design | "Let's run `eg-brainstorm` for <rough idea>" | Multiple goldfish in parallel generate divergent ideas. All questions via `ask_user`. Hands off to `eg-prd` or `eg-new-feature`. |
| Product Requirements Doc | "Let's write an `eg-prd` for <feature>" | Codebase grounding → structured gap-filling → deep research with parallel goldfish → synthesized PRD. Saves to `[BOOTSTRAP: prd path, e.g. `docs/prds/`]`. |
| Bug fix flow | "Run `eg-fix-bug` for <description \| #issue>" | Bug fix flow: problem doc → goldfish diagnosis check → failing test → fix → `eg-precommit-review` → test gate. |
| Feature flow | "Run `eg-new-feature` for <description>" | Feature flow: scope confirm → design doc → goldfish design check → implement → `eg-precommit-review` → test gate. [BOOTSTRAP: one-line summary of stack-specific design rubric items.] |
| Independent review | "Run `eg-precommit-review`" | Local independent-review loop on the pending diff ([BOOTSTRAP: pre-flight summary]). |

You provide a brief instruction; Gemini writes the doc back at you. Examples:

> Let's do an `eg-brainstorm` for [BOOTSTRAP: a short, realistic raw idea for this project]
> Please run the `eg-new-feature` flow for [BOOTSTRAP: a short, realistic feature description for this project]
> Time for an `eg-precommit-review`

Each skill workflow stops short of committing. Authorize the commit explicitly when ready. [BOOTSTRAP: commit-policy reminder if the project has one]
<<<SNIPPET_END>>>
```
