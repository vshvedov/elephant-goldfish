# Elephant/Goldfish (Claude Code, Codex)

<img width="960" height="540" alt="1_kppt5IZmL1DRzrQub3DPyQ" src="https://github.com/user-attachments/assets/93e98eac-31c7-420b-8169-867a6c95f389" />

A reusable workflow for software work with Claude Code and Codex, built around the elephant/goldfish pattern from [Daniel Rensin's article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874).

---

## How to install

### Claude Code

In your target repo, open a Claude Code session and paste this message:

> Fetch the elephant-goldfish bootstrap procedure with
> `gh api repos/vshvedov/elephant-goldfish/contents/claude/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'`,
> then follow the procedure to set up the elephant/goldfish workflow here.

The root `BOOTSTRAP.md` remains as a compatibility entrypoint for older install snippets, but new Claude installs should fetch `claude/BOOTSTRAP.md` directly.

### Codex

In the same target repo, open a Codex session and paste this message:

> Fetch the Codex elephant-goldfish bootstrap procedure with
> `gh api repos/vshvedov/elephant-goldfish/contents/codex/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'`,
> then follow the procedure to set up the Codex elephant/goldfish workflow here, preserving any existing Claude Code setup.

The two installs are additive. Claude Code gets `.claude/commands/` and `CLAUDE.md`; Codex gets a repo-local plugin plus `AGENTS.md`. They can live in the same repo and should mirror the same project conventions.

## What you get

Five workflow commands for each agent:

| Stage | Claude Code | Codex |
|---|---|---|
| Brainstorm | `/eg-brainstorm` | `/elephant-goldfish-codex:eg-brainstorm` |
| PRD | `/eg-prd` | `/elephant-goldfish-codex:eg-prd` |
| Bug fix | `/eg-fix-bug` | `/elephant-goldfish-codex:eg-fix-bug` |
| New feature | `/eg-new-feature` | `/elephant-goldfish-codex:eg-new-feature` |
| Precommit review | `/eg-precommit-review` | `/elephant-goldfish-codex:eg-precommit-review` |

Claude Code uses the templates in [claude/](claude/), installs into `<target>/.claude/commands/`, and injects a "Working with Claude Code" section into `CLAUDE.md`.

Codex uses the templates in [codex/](codex/), installs a project-local plugin under `<target>/plugins/elephant-goldfish-codex/`, registers it in `<target>/.agents/plugins/marketplace.json`, and injects a "Working with Codex (elephant/goldfish)" section into `AGENTS.md`.

Both bootstraps inspect the target stack and customize the generic templates for the detected language, test tiers, browser/simulator validation path, project-specific review gotchas, and commit convention. See [Bootstrap a new repo](#bootstrap-a-new-repo) below for the full procedure.

**Why `gh api` instead of `git clone`?** No working copy left lying around — just text streamed in, customized, and written into the target. Cleaner than clone for a one-shot setup, and works the same whether this repo is public or private.

---

## The pattern

### Elephant

Your working session: Claude Code or Codex with full context — this conversation, the repo instructions (`CLAUDE.md` for Claude, `AGENTS.md` for Codex), files read in recent turns, and decisions already made together. The elephant carries the institutional memory.

### Goldfish

A fresh subagent spawned with no prior context. It receives only what you hand it: a problem statement, a design doc, or a diff. It has no idea what you've been thinking. That's the point.

### The asymmetry is the test

If a goldfish, given only the problem statement, lands somewhere different from where the elephant started, that disagreement is the cheapest signal you'll get that you were anchored. If a goldfish, given only the design doc, can't implement the same thing you intended, the doc is wrong — not the goldfish. **Design is the new code.** When AI generates more code than humans can review, the human-readable doc becomes the primary artifact, and a fresh reader who can act on it alone is the cheapest correctness check available.

---

## The pipeline

> `/eg-brainstorm` produces a **concept**. `/eg-prd` turns a concept into **requirements**. `/eg-new-feature` and `/eg-fix-bug` produce **code**. `/eg-precommit-review` produces **validated code**. Each upstream stage feeds the next.

```mermaid
flowchart LR
    R(["rough idea"]) --> A["/eg-brainstorm"]
    A -- concept --> B["/eg-prd"]
    B -- PRD --> C["/eg-new-feature"]
    BG(["bug, issue, repro"]) --> D["/eg-fix-bug"]
    C -- code change --> E["/eg-precommit-review"]
    D -- code change --> E
    E -- validated change --> F(["commit"])
```

You don't have to start at the top. Pick the stage that matches what you have:

| You have | Start with | The output |
|---|---|---|
| A half-formed thought, no direction yet | `/eg-brainstorm` | A concepts brief; pick a direction. |
| A direction but no requirements | `/eg-prd` | A PRD: scope, users, metrics, open questions. |
| A clear feature to build | `/eg-new-feature` | Implemented + reviewed code, ready to commit. |
| A bug or a `#<issue>` | `/eg-fix-bug` | A failing-test-driven fix, ready to commit. |
| A diff already in hand | `/eg-precommit-review` | A reviewer-cleared diff, ready to commit. |

### How each stage uses the pattern

**`/eg-brainstorm`** inverts the pattern. Instead of one goldfish stress-testing the elephant, multiple goldfish run in parallel — each with a different lens (technical, business, UX, contrarian, market research) — to generate divergent ideas the elephant synthesizes into a concepts brief. In Claude, structured clarifying questions go through `AskUserQuestion`; in Codex, they use structured user input when available or concise targeted chat questions.

**`/eg-prd`** uses two waves of goldfish. First, exploration goldfish ground the request in the existing codebase. Then, after structured gap-filling Q&A with the user, research goldfish run in parallel across distinct lenses. Claude templates reference Chrome MCP where appropriate; Codex templates reference Browser Use / the in-app browser. The elephant synthesizes a PRD with explicit Open Questions for whatever the user deferred.

**`/eg-new-feature`** uses one goldfish to stress-test the design doc the elephant drafted. If the goldfish can't implement the same thing from the doc alone, the doc gets revised. Implementation only starts after the doc is "design ready." Then the same diff goes through `/eg-precommit-review`.

**`/eg-fix-bug`** uses one goldfish to diagnose the bug from only the symptom and repro. The elephant's hypothesis stays hidden until after the goldfish reports — convergence buys confidence; divergence is signal. The bug gets captured as a failing test before any fix is written.

**`/eg-precommit-review`** is itself a goldfish. It sees only the diff, not the conversation. Findings are triaged round by round, with a hard cap and a structured user escalation if the loop doesn't converge.

---

## Commands

| Intent | Claude Code command | Codex command |
|---|---|---|
| Early-stage concept design | `/eg-brainstorm <rough idea>` | `/elephant-goldfish-codex:eg-brainstorm <rough idea>` |
| PRD from idea / feature / issue | `/eg-prd <idea \| feature \| #issue>` | `/elephant-goldfish-codex:eg-prd <idea \| feature \| #issue>` |
| Bug fix flow | `/eg-fix-bug <description \| #issue \| URL>` | `/elephant-goldfish-codex:eg-fix-bug <description \| #issue \| URL>` |
| Feature flow | `/eg-new-feature <description \| #issue \| URL>` | `/elephant-goldfish-codex:eg-new-feature <description \| #issue \| URL>` |
| Independent diff review | `/eg-precommit-review` | `/elephant-goldfish-codex:eg-precommit-review` |

Implementation commands (`/eg-fix-bug`, `/eg-new-feature`) stop short of committing. The user authorizes the commit explicitly when ready.

You give a one-liner; the agent writes the doc back at you. **You don't author docs by hand.** Most docs live in chat. They land on disk only when there's a future-you reason to keep them — a substantial feature, a new subsystem, a saved brainstorm brief, a PRD that will be revisited.

---

## Bootstrap a new repo

(See [How to install](#how-to-install) at the top for the one-line invocation.)

After you give Claude the `gh api` instruction, Claude will:

1. Read [claude/BOOTSTRAP.md](claude/BOOTSTRAP.md) for the procedure.
2. Inspect the target repo's stack — `package.json`, `Gemfile`, `pubspec.yaml`, `pyproject.toml`, `mise.toml`, `.tool-versions`, CI config, etc.
3. Read the target's `CLAUDE.md` if it exists; otherwise propose creating one.
4. Customize the five generic templates in [claude/commands/](claude/commands/) for the detected stack: pre-flight commands, test tier picks, browser-validation path, stack-specific "Hunt for" items in the reviewer prompt, and the PRD save location for `/eg-prd`.
5. Drop the tailored files into `<target>/.claude/commands/`.
6. Inject the "Working with Claude Code" section ([claude/snippet.md](claude/snippet.md)) into the target's `CLAUDE.md`.
7. Print a summary and stop short of committing.

The customized commands keep the same shape (problem doc, goldfish, failing test, review, gate) but speak the target's language: `mise exec ... rails test` for Rails, `flutter test` for Flutter, `npm test && npm run test:e2e` for Node, and so on.

After you give Codex the `gh api` instruction, Codex will:

1. Read [codex/BOOTSTRAP.md](codex/BOOTSTRAP.md) for the procedure.
2. Inspect the target repo's `AGENTS.md`, `CLAUDE.md`, manifests, CI config, and recent commits.
3. Customize the Codex templates in [codex/commands/](codex/commands/) for the detected stack.
4. Create `<target>/plugins/elephant-goldfish-codex/` with `.codex-plugin/plugin.json` and the five command files.
5. Register the project-local plugin in `<target>/.agents/plugins/marketplace.json`.
6. Inject the "Working with Codex (elephant/goldfish)" section ([codex/agents-md-snippet.md](codex/agents-md-snippet.md)) into `AGENTS.md`.
7. Print a summary and stop short of committing.

The Codex bootstrap explicitly preserves `.claude/commands/*` and `CLAUDE.md`.

---

## Project-specific commands

Some projects need a stack-specific verb the generic commands don't cover — for example, a creative-coding project that ships modular plugins might want `/eg-new-plugin` with a recipe covering the manifest, DSP, registration steps, and a hardware-style verification pass. A SaaS with a heavy schema layer might want `/eg-new-migration` with a backfill rubric.

Pattern:

1. Copy `eg-new-feature.md` from the relevant target adapter as the starting shape: `.claude/commands/` for Claude Code, or `plugins/elephant-goldfish-codex/commands/` for Codex.
2. Tailor: replace the design rubric with the project-specific recipe (the architectural invariants, the canonical "how to add one of these" steps from `CLAUDE.md` / `AGENTS.md`, the verification path).
3. Add a `Routing` note at the top of the generic new-feature command so users and agents know when to switch.

Use the `eg-` prefix for any project-specific command — keeps the namespace consistent so the elephant/goldfish set is grep-able and won't collide with generic verbs like `/prd` or `/research`.

The command stays in the target repo's agent-specific command folder only — it is project-specific and does not belong in this template repo unless it is broadly reusable.

---

## Why a separate repo

So the templates evolve in one place. When you tighten `/eg-precommit-review`'s reviewer prompt because the goldfish kept missing a class of bug, you do it here once, and re-bootstrap the projects that pull from this. Projects can pin to a specific commit if they want a frozen version.

---

## License

MIT. Use it, fork it, send PRs.
