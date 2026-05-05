# Snippet to inject into target AGENTS.md

This is the section that gets added to the target repo's `AGENTS.md` during Codex bootstrap. Tailor the placeholders, then inject. Do not include this header line or the surrounding text — only what's between the `<<<SNIPPET_START>>>` and `<<<SNIPPET_END>>>` markers.

```
<<<SNIPPET_START>>>
## Working with Codex (elephant/goldfish)

This repo has a project-local Codex plugin at [plugins/elephant-goldfish-codex/](plugins/elephant-goldfish-codex/) with five skills that mirror the Claude Code elephant/goldfish workflow. Codex does not currently support project-defined custom slash commands, so invoke these workflows as skills, for example `Use $eg-precommit-review to review my pending changes` or `Use $eg-new-feature to build <feature>`. For composer autocomplete in current Codex app builds, the skill folders are also symlinked into `${CODEX_HOME:-~/.codex}/skills/eg-*`; the repo-local plugin remains the source of truth. The elephant is the current Codex thread with full repo and conversation context. A goldfish is a fresh Codex subagent, spawned with only the problem doc, design doc, research seed, or diff it needs.

| Skill | When to use |
|---|---|
| `$eg-brainstorm <rough idea>` | Early-stage concept design. Multiple fresh goldfish run in parallel with different lenses, then the elephant synthesizes a concepts brief. |
| `$eg-prd <idea \| feature description>` | Build a PRD from a rough idea: codebase grounding, gap-filling, optional research, and synthesized requirements. Saves to `[BOOTSTRAP: prd path, e.g. `docs/prds/`]` when requested. |
| `$eg-fix-bug <description \| #issue \| URL>` | Bug fix flow: problem doc, independent diagnosis, failing regression test, fix, review, and test gate. |
| `$eg-new-feature <description \| #issue \| URL>` | Feature flow: scope confirmation, design doc, goldfish design check, implementation, review, and test gate. [BOOTSTRAP: one-line stack-specific design rubric summary.] |
| `$eg-precommit-review [focus]` | Local independent-review loop over pending changes, with pre-flight checks and a fresh reviewer that sees the diff cold. |
[BOOTSTRAP: if the project has a stack-specific skill like `$eg-new-module`, add a row for it here.]

Question discipline: use Codex structured user input when available; otherwise ask concise, targeted chat questions. Do not replace structured choices with open-ended prompts when the answer is enumerable.

Browser validation: [BOOTSTRAP: browser validation paragraph — for web apps, use the Browser Use / in-app browser plugin against `[BOOTSTRAP: dev URL]`, starting the server via `[BOOTSTRAP: dev start command]` if needed; for mobile, use the simulator/device path; for backend-only, omit.]

Each elephant/goldfish skill stops short of committing. The user authorizes commits explicitly. [BOOTSTRAP: commit-policy reminder if the project has one.]
<<<SNIPPET_END>>>
```
