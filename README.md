# Elephant/Goldfish (Claude Code, Codex, Gemini CLI)

<img width="960" height="540" alt="1_kppt5IZmL1DRzrQub3DPyQ" src="https://github.com/user-attachments/assets/93e98eac-31c7-420b-8169-867a6c95f389" />

A reusable workflow for software work with Claude Code, Codex, and Gemini CLI, built around the elephant/goldfish pattern from [Dave Rensin's article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874).

---

## Why?

Most of the AI agents are working fine today. Some of them better than others. Why have you added something to a verified workflow? 

> There's an easy answer. Imagine this: You're a manager, and you have two hires: a Junior Developer and a Senior Staff Engineer. Both will be producing the code. The only difference is the kind of code and architecture you end up with. On one hand, this approach allows you to efficiently close the gap in your thinking and leverage the model's expertise before code writing begins, while you're in control. On the other hand, the Elephant/Goldfish pattern allows the AI to validate its own ideas, stay in contact with you, and stay up to date on the requirements.

> You're shifting the pipeline from "write me the code" to "think about what I missed, use a second opinion, collaborate, then write and test after".

The price is the higher token consumption and longer irrational work. Be warned.

## How to install

### Claude Code

<img width="200" height="200" alt="claude-ai-200" src="https://github.com/user-attachments/assets/8f0ed03d-55ca-48c6-b1b5-96df712a145e" />


In your target repo, open a Claude Code session and paste this message:

```
Fetch the elephant-goldfish bootstrap procedure with
`gh api repos/vshvedov/elephant-goldfish/contents/claude/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'`,
then follow the procedure to set up the elephant/goldfish workflow here, preserving any existing setups for other AIs.
```

When done, reload Claude Code session (restart the app) and start typing:

```
/eg-...

```

You should see the list of all `eg-` commands:

<img width="846" height="562" alt="Screenshot 2026-05-05 at 3 13 40 PM" src="https://github.com/user-attachments/assets/eac5740f-71d0-426a-80c9-a71941690d24" />

The root `BOOTSTRAP.md` remains as a compatibility entrypoint for older install snippets, but new Claude installs should fetch `claude/BOOTSTRAP.md` directly.

### Codex (beta)

<img width="200" height="200" alt="codex-color-200" src="https://github.com/user-attachments/assets/4a16e916-2a3d-498e-8d25-4017ab09cefc" />


In the same target repo, open a Codex session and paste this message:

```
Fetch the Codex elephant-goldfish bootstrap procedure with
`gh api repos/vshvedov/elephant-goldfish/contents/codex/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'`,
then follow the procedure to set up the Codex elephant/goldfish workflow here, preserving any existing setups for other AIs.
```

When done, you'll have a set of "Elephant/Goldfish" Codex skills. Start typing:

```
$eg...
```

You should see the list of all e/g skills:

<img width="791" height="383" alt="Screenshot 2026-05-05 at 3 13 57 PM" src="https://github.com/user-attachments/assets/81706de4-3da2-496f-88b4-f5f836f8f535" />


### Gemini CLI (beta)

<img width="200" height="200" alt="gemini-200" src="https://github.com/user-attachments/assets/c837370b-d457-4717-ad30-30ea9beca77a" />


In your target repo, open a Gemini CLI session and paste this message:

```
Fetch the Gemini CLI elephant-goldfish bootstrap procedure with
`gh api repos/vshvedov/elephant-goldfish/contents/gemini/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'`,
then follow the procedure to set up the Gemini CLI elephant/goldfish workflow here, preserving any existing setups for other AIs.
```

When done, you'll have a set of "Elephant/Goldfish" Gemini CLI skills. Reload first:

```
/skills reload
```

Then start typing:

```
/eg...
```

You should see the list of all e/g skills:

<img width="960" height="283" alt="Screenshot 2026-05-05 at 3 11 26 PM" src="https://github.com/user-attachments/assets/eaf80bf9-eb35-4ed9-a869-1d434659f0e5" />

---

*The installs are additive. Claude Code gets project-local `.claude/commands/` and `CLAUDE.md`; Codex gets shared user skills installed directly into `${CODEX_HOME:-~/.codex}/skills/`; Gemini CLI gets local workspace Skills in `.gemini/skills/` plus `GEMINI.md`. They can live side by side and should mirror the same workflow conventions.*

---

## Adaptive Injection

For Claude Code and Gemini CLI, this repository uses **Adaptive Injection**. When you bootstrap a repository:
1. The AI analyzes your **local stack** (languages, frameworks, test runners).
2. It fetches **generic templates** from this repo.
3. It **contextualizes** those templates, replacing `[BOOTSTRAP: ...]` markers with your actual project commands.

This ensures that `/eg-fix-bug` in a Rails app knows to run `bundle exec rails test`, while in a Flutter app it runs `flutter test`.

Codex is different: the `eg-*` workflows are shared user skills installed once into `~/.codex/skills`. They inspect the current repo at runtime instead of being rewritten for each project. That avoids one project's bootstrap overwriting another project's global Codex skills.

## Keeping Up to Date

Since Claude/Gemini local commands are customized, you can't simply overwrite them when this repository updates. To sync the latest logic while preserving your local configuration:

1. Open [PROMPTS.md](./PROMPTS.md).
2. Copy the **"Update Elephant/Goldfish Patterns"** prompt.
3. Paste it into your AI agent (Claude, Gemini, or Codex) inside your bootstrapped project.

The AI will fetch the latest templates, identify your local adaptations, and perform a "smart merge" to bring in new workflow improvements without breaking your local build commands. For Codex, rerun the Codex bootstrap to refresh the shared `~/.codex/skills/eg-*` directories.

---

## What you get

Five workflow commands/skills for each agent:

| Stage | Claude Code | Codex | Gemini CLI |
|---|---|---|---|
| Brainstorm | `/eg-brainstorm` | `Use $eg-brainstorm ...` | `eg-brainstorm` Skill |
| PRD | `/eg-prd` | `Use $eg-prd ...` | `eg-prd` Skill |
| Bug fix | `/eg-fix-bug` | `Use $eg-fix-bug ...` | `eg-fix-bug` Skill |
| New feature | `/eg-new-feature` | `Use $eg-new-feature ...` | `eg-new-feature` Skill |
| Precommit review | `/eg-precommit-review` | `Use $eg-precommit-review ...` | `eg-precommit-review` Skill |

Claude and Gemini bootstraps inspect the target stack and customize local templates for the detected language, test tiers, browser/simulator validation path, project-specific review gotchas, and commit convention. Codex installs shared skills once; those skills inspect the current repo at runtime. See [Bootstrap a new repo](#bootstrap-a-new-repo) below for the full procedure.

---

## The pattern

### Elephant

Your working session: Claude Code, Codex, or Gemini CLI with full context — this conversation, the repo instructions (`CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`), files read in recent turns, and decisions already made together. The elephant carries the institutional memory.

### Goldfish

A fresh subagent spawned with no prior context. It receives only what you hand it: a problem statement, a design doc, or a diff. It has no idea what you've been thinking. That's the point.

### The asymmetry is the test

If a goldfish, given only the problem statement, lands somewhere different from where the elephant started, that disagreement is the cheapest signal you'll get that you were anchored. If a goldfish, given only the design doc, can't implement the same thing you intended, the doc is wrong — not the goldfish. **Design is the new code.** When AI generates more code than humans can review, the human-readable doc becomes the primary artifact, and a fresh reader who can act on it alone is the cheapest correctness check available.

---

## The pipeline

> `eg-brainstorm` produces a **concept**. `eg-prd` turns a concept into **requirements**. `eg-new-feature` and `eg-fix-bug` produce **code**. `eg-precommit-review` produces **validated code**. Each upstream stage feeds the next.

```mermaid
flowchart LR
    R(["rough idea"]) --> A["eg-brainstorm"]
    A -- concept --> B["eg-prd"]
    B -- PRD --> C["eg-new-feature"]
    BG(["bug, issue, repro"]) --> D["eg-fix-bug"]
    C -- code change --> E["eg-precommit-review"]
    D -- code change --> E
    E -- validated change --> F(["commit"])
```

You don't have to start at the top. Pick the stage that matches what you have:

| You have | Start with | The output |
|---|---|---|
| A half-formed thought, no direction yet | `eg-brainstorm` | A concepts brief; pick a direction. |
| A direction but no requirements | `eg-prd` | A PRD: scope, users, metrics, open questions. |
| A clear feature to build | `eg-new-feature` | Implemented + reviewed code, ready to commit. |
| A bug or a `#<issue>` | `eg-fix-bug` | A failing-test-driven fix, ready to commit. |
| A diff already in hand | `eg-precommit-review` | A reviewer-cleared diff, ready to commit. |

### How each stage uses the pattern

**`eg-brainstorm`** inverts the pattern. Instead of one goldfish stress-testing the elephant, multiple goldfish run in parallel — each with a different lens (technical, business, UX, contrarian, market research) — to generate divergent ideas the elephant synthesizes into a concepts brief. Agents use structured clarifying questions (`AskUserQuestion`, `ask_user`, or structured prompts) to interact with the user.

**`eg-prd`** uses two waves of goldfish. First, exploration goldfish ground the request in the existing codebase. Then, after structured gap-filling Q&A with the user, research goldfish run in parallel across distinct lenses. The elephant synthesizes a PRD with explicit Open Questions for whatever the user deferred.

**`eg-new-feature`** uses one goldfish to stress-test the design doc the elephant drafted. If the goldfish can't implement the same thing from the doc alone, the doc gets revised. Implementation only starts after the doc is "design ready." Then the same diff goes through `eg-precommit-review`.

**`eg-fix-bug`** uses one goldfish to diagnose the bug from only the symptom and repro. The elephant's hypothesis stays hidden until after the goldfish reports — convergence buys confidence; divergence is signal. The bug gets captured as a failing test before any fix is written.

**`eg-precommit-review`** is itself a goldfish. It sees only the diff, not the conversation. Findings are triaged round by round, with a hard cap and a structured user escalation if the loop doesn't converge.

---

## Commands And Skills

| Intent | Claude Code | Codex | Gemini CLI |
|---|---|---|---|
| Early-stage concept design | `/eg-brainstorm <rough idea>` | `Use $eg-brainstorm to brainstorm <rough idea>` | Invoke `eg-brainstorm` skill |
| PRD from idea / feature / issue | `/eg-prd <idea \| feature \| #issue>` | `Use $eg-prd to write a PRD for <idea \| feature \| #issue>` | Invoke `eg-prd` skill |
| Bug fix flow | `/eg-fix-bug <description \| #issue \| URL>` | `Use $eg-fix-bug to fix <description \| #issue \| URL>` | Invoke `eg-fix-bug` skill |
| Feature flow | `/eg-new-feature <description \| #issue \| URL>` | `Use $eg-new-feature to build <description \| #issue \| URL>` | Invoke `eg-new-feature` skill |
| Independent diff review | `/eg-precommit-review` | `Use $eg-precommit-review to review my pending changes` | Invoke `eg-precommit-review` skill |

Implementation flows (`eg-fix-bug`, `eg-new-feature`) stop short of committing. The user authorizes the commit explicitly when ready.

Codex note: current Codex builds do not support project-defined custom slash commands, so `/eg-*` and `/elephant-goldfish-codex:eg-*` are not expected to appear in the slash-command menu. Use `$eg-*` skill mentions instead.

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
2. Install the shared Codex skill folders from [codex/skills/](codex/skills/) directly into `${CODEX_HOME:-~/.codex}/skills/eg-*` as real directories.
3. Replace old project-local symlinks if present, while preserving unrelated user skills.
4. Optionally inject the "Working with Codex (elephant/goldfish)" section ([codex/agents-md-snippet.md](codex/agents-md-snippet.md)) into the current project's `AGENTS.md`.
5. Print a summary and remind you to start a new Codex session or reload the app if `$eg` autocomplete has not refreshed.

After you give Gemini CLI the `gh api` instruction, it will:

1. Read [gemini/BOOTSTRAP.md](gemini/BOOTSTRAP.md) for the procedure.
2. Inspect the target repo's stack.
3. Customize the Gemini SKILL templates in [gemini/commands/](gemini/commands/).
4. Create workspace-scoped skill folders under `<target>/.gemini/skills/`.
5. Install the skills locally via the `gemini skills install` command.
6. Inject the "Working with Gemini CLI" snippet into `GEMINI.md`.
7. Print a summary and remind you to run `/skills reload` to activate them.

All bootstraps explicitly preserve other agents' existing files. Codex does not create project-local plugin or marketplace files.

---

## Project-specific Commands And Skills

Some projects need a stack-specific verb the generic workflows don't cover — for example, a creative-coding project that ships modular plugins might want `eg-new-plugin` with a recipe covering the manifest, DSP, registration steps, and a hardware-style verification pass. A SaaS with a heavy schema layer might want `eg-new-migration` with a backfill rubric.

Pattern:

1. Copy `eg-new-feature.md` from the relevant target adapter as the starting shape: `.claude/commands/` for Claude Code, `${CODEX_HOME:-~/.codex}/skills/eg-new-feature/SKILL.md` for Codex, or `.gemini/skills/` for Gemini CLI.
2. Tailor: replace the design rubric with the project-specific recipe (the architectural invariants, the canonical "how to add one of these" steps from `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`, the verification path).
3. Add a `Routing` note at the top of the generic new-feature command or skill so users and agents know when to switch.

Use the `eg-` prefix for any project-specific command or skill — keeps the namespace consistent so the elephant/goldfish set is grep-able and won't collide with generic verbs like `/prd` or `/research`.

The command or skill stays in the target repo's agent-specific folder only — it is project-specific and does not belong in this template repo unless it is broadly reusable.

---

## Why a separate repo

So the templates evolve in one place. When you tighten `eg-precommit-review`'s reviewer prompt because the goldfish kept missing a class of bug, you do it here once, and re-bootstrap the projects that pull from this. Projects can pin to a specific commit if they want a frozen version.

---

## License

MIT. Use it, fork it, send PRs.
