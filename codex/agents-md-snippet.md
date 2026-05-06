# Snippet to inject into target AGENTS.md

This optional section can be added to a target repo's `AGENTS.md` during Codex bootstrap. It documents globally installed user skills. Do not include this header line or the surrounding text — only what's between the `<<<SNIPPET_START>>>` and `<<<SNIPPET_END>>>` markers.

```
<<<SNIPPET_START>>>
## Working with Codex (elephant/goldfish)

The elephant/goldfish Codex workflows are installed as global user skills under `${CODEX_HOME:-~/.codex}/skills/eg-*`. Codex does not currently support project-defined custom slash commands, so invoke these workflows as skills, for example `Use $eg-precommit-review to review my pending changes` or `Use $eg-new-feature to build <feature>`. The elephant is the current Codex thread with full repo and conversation context. A goldfish is a fresh Codex subagent, spawned with only the problem doc, design doc, research seed, or diff it needs.

| Skill | When to use |
|---|---|
| `$eg-brainstorm <rough idea>` | Early-stage concept design. Multiple fresh goldfish run in parallel with different lenses, then the elephant synthesizes a concepts brief. |
| `$eg-prd <idea \| feature description>` | Build a PRD from a rough idea: codebase grounding, gap-filling, optional research, and synthesized requirements. Infers a project-appropriate save path when requested. |
| `$eg-fix-bug <description \| #issue \| URL>` | Bug fix flow: problem doc, independent diagnosis, failing regression test, fix, review, and test gate. |
| `$eg-new-feature <description \| #issue \| URL>` | Feature flow: scope confirmation, design doc, goldfish design check, implementation, review, and test gate. Reads AGENTS.md/CLAUDE.md and repo manifests for project guardrails. |
| `$eg-precommit-review [focus]` | Local independent-review loop over pending changes, with pre-flight checks and a fresh reviewer that sees the diff cold. |
Question discipline: use Codex structured user input when available; otherwise ask concise, targeted chat questions. Do not replace structured choices with open-ended prompts when the answer is enumerable.

Browser validation: for web apps, use Browser Use / the in-app browser against the dev server documented by the repo. For mobile, use the simulator/device path. For backend-only projects, use tests, curl/API checks, or logs.

Each elephant/goldfish skill stops short of committing. The user authorizes commits explicitly.
<<<SNIPPET_END>>>
```
