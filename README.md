# Elephant/Goldfish for Claude Code

<img width="960" height="540" alt="1_kppt5IZmL1DRzrQub3DPyQ" src="https://github.com/user-attachments/assets/93e98eac-31c7-420b-8169-867a6c95f389" />

A reusable workflow for software work with Claude Code, built around the elephant/goldfish pattern from [Daniel Rensin's article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874).

---

## 🚀 Quick start — bootstrap a new repo

In your target repo, in a Claude Code session, paste this:

```
Fetch the elephant-goldfish bootstrap procedure with:
  gh api repos/vshvedov/elephant-goldfish/contents/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'
Then follow the procedure to set up the elephant/goldfish workflow here.
```

That's it. Claude streams the procedure text directly through `gh api`, inspects your stack, fetches the four command templates and the CLAUDE.md snippet the same way, customizes them, drops them into `<target>/.claude/commands/`, and updates your `CLAUDE.md`. See [Bootstrap a new repo](#bootstrap-a-new-repo) below for the full procedure.

> **Why `gh api`, not `git clone`?** No working copy left lying around — just text streamed in, customized, and written into the target. Cleaner than clone for a one-shot setup.

---

## The pattern in one paragraph

The **elephant** is your working session — Claude Code with full context: the conversation, CLAUDE.md, recent file reads, your last few decisions. The **goldfish** is a fresh subagent with no prior context that stress-tests a problem doc, a design doc, or a diff. The asymmetry is the point: you are anchored to your hypothesis; a goldfish is not. If a goldfish, given only the problem statement, lands somewhere different from where you started, that disagreement is the cheapest signal you'll get that you were anchored. If a goldfish, given only the design doc, can't implement the same thing you intended, the doc is wrong, not the goldfish. **Design is the new code.** When AI generates more code than humans can review, the human-readable doc becomes the primary artifact.

## What this repo gives you

Four slash commands that wrap that pattern around real work:

| Command | What it does |
|---|---|
| `/brainstorm <rough idea>` | Early-stage concept design. **Inverts** the pattern: spawns multiple goldfish in parallel, each with a different lens (technical / business / UX / contrarian / market research), free to web-search. Elephant synthesizes a concepts brief. All clarifying questions go through `AskUserQuestion`. |
| `/fix-bug <description \| #issue \| URL>` | Problem doc → goldfish diagnosis check → failing test → fix → `/precommit-review` → test gate. |
| `/new-feature <description \| #issue \| URL>` | Scope confirm → design doc → goldfish design check → implement → `/precommit-review` → test gate. |
| `/precommit-review` | Local independent-review loop on the pending diff (lint + typecheck + tests as pre-flight, then a fresh subagent reviews the diff cold). |

`/brainstorm` produces a concept; `/new-feature` and `/fix-bug` produce code; `/precommit-review` validates code. The first one feeds the second.

Each implementation command stops short of committing. The user authorizes the commit explicitly when ready.

You give a one-liner; Claude writes the doc back at you. **You don't author docs by hand.** The doc lives in chat for most work; on disk only when there's a future-you reason to keep it (substantial feature, new subsystem, saved brainstorm brief).

## Bootstrap a new repo

(See the [Quick start](#-quick-start--bootstrap-a-new-repo) at the top for the one-line invocation.)

Once you give Claude the `gh repo clone` instruction, Claude will:
1. Read [BOOTSTRAP.md](BOOTSTRAP.md) for the procedure.
2. Inspect the target repo's stack (package.json / Gemfile / pubspec.yaml / pyproject / etc.).
3. Read the target's CLAUDE.md if it exists; otherwise plan to create one.
4. Customize the four generic templates in [commands/](commands/) for the detected stack: pre-flight commands, test tier picks, browser-validation path, and stack-specific "Hunt for" items in the reviewer prompt.
5. Drop the tailored files into `<target>/.claude/commands/`.
6. Inject the "Working with Claude Code" section ([claude-md-snippet.md](claude-md-snippet.md)) into the target's CLAUDE.md.
7. Print a summary and stop short of committing.

The customized commands keep the same shape (problem doc, goldfish, failing test, review, gate) but speak the target's language: `mise exec ... rails test` for Rails, `flutter test` for Flutter, `npm test && npm run test:e2e` for Node, etc.

## Adding a project-specific command

Some projects need a stack-specific verb the generic commands don't cover — for example, a creative-coding project that ships modular plugins might want `/new-plugin` with a recipe covering the manifest, DSP, registration steps, and a mandatory hardware-style verification pass. A SaaS with a heavy schema layer might want `/new-migration` with a backfill rubric. Pattern:

1. Copy `commands/new-feature.md` from your target as the starting shape.
2. Tailor: replace the design rubric with the project-specific recipe (the architectural invariants, the canonical "how to add one of these" steps from your CLAUDE.md, the verification path).
3. Add a `Routing` note at the top of `/new-feature.md` so users (and Claude) know when to switch.

The command stays in `<target>/.claude/commands/` only — it's project-specific, doesn't belong in this template repo.

## Why a separate repo

So the templates evolve in one place. When you tighten `/precommit-review`'s reviewer prompt because the goldfish kept missing a class of bug, you do it here once, and re-bootstrap the projects that pull from this. Projects can also pin to a specific commit if they want a frozen version.

## License

MIT. Use it, fork it, send PRs.
