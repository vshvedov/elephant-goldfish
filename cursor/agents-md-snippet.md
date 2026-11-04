# Snippet to inject into target AGENTS.md

This is the section that gets added to the target repo's `AGENTS.md` during Cursor bootstrap. Tailor the placeholders, then inject. Do not include this header line or the surrounding text — only what's between the `<<<SNIPPET_START>>>` and `<<<SNIPPET_END>>>` markers.

```
<<<SNIPPET_START>>>
## Working with Cursor (elephant/goldfish skills)

Five skills in [.cursor/skills/](.cursor/skills/) wrap an "elephant/goldfish" workflow inspired by [this article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874): the "elephant" is the current Cursor Agent chat with full context (this AGENTS.md, repo state, conversation history); the "goldfish" is a fresh subagent launched via the `Task` tool with no prior context. For implementation work the goldfish stress-tests a problem/design doc or a diff. For brainstorming and PRD writing, multiple goldfish run in parallel with different lenses to generate divergent ideas or research findings the elephant synthesizes.

Invoke any skill by typing `/` in Agent chat and picking the name, e.g. `/eg-fix-bug`, or by referencing it naturally ("use the eg-fix-bug skill").

| Skill | When to use |
|---|---|
| `/eg-brainstorm <rough idea>` | Early-stage concept design. Multiple goldfish in parallel (technical / business / UX / contrarian / market research), web search optional, elephant synthesizes a concepts brief. All questions via `AskQuestion`. Hands off to `/eg-prd` or `/eg-new-feature` if you pick a direction. |
| `/eg-prd <idea \| feature description>` | Build a thorough PRD: codebase grounding via parallel `Task`-launched explore goldfish → structured gap-filling via `AskQuestion` → deep research with parallel goldfish (web optional) → synthesized PRD. Saves to `[BOOTSTRAP: prd path, e.g. `docs/prds/`]`, persists durable nuggets to AGENTS.md, and/or hands off to `/eg-new-feature`. |
| `/eg-fix-bug <description \| #issue \| URL>` | Bug fix flow: problem doc → goldfish diagnosis check via `Task` → failing test → fix → `/eg-precommit-review` → test gate. Skips ceremony for trivial diffs. |
| `/eg-new-feature <description \| #issue \| URL>` | Feature flow: scope confirm → design doc → three-goldfish design check (comprehension + critic + readiness) launched as parallel `Task` calls → implement → `/eg-precommit-review` → test gate. [BOOTSTRAP: one-line summary of stack-specific design rubric items, e.g. "Multi-tenant scoping and CanCanCan checks are part of the design rubric." for Rails, or "Lifecycle/dispose, BLoC scope, cache invalidation, and platform-divergence checks." for Flutter.] |
| `/eg-precommit-review [focus]` | Local independent-review loop on the pending diff ([BOOTSTRAP: pre-flight summary, e.g. "Brakeman + MiniTest + Playwright"]). Replaces back-and-forth with PR bots — by the time the PR opens, the substantive review is already settled. |
[BOOTSTRAP: if the project has a stack-specific verb like `/eg-new-module`, add a row for it here.]

The goldfish is implemented via Cursor's `Task` tool with `subagent_type: "explore"` (narrow codebase lookups) or `"generalPurpose"` (multi-surface work). The elephant is whatever Cursor Agent chat invoked the skill. Structured user questions use the `AskQuestion` tool; free-form chat is reserved for unbounded answers after a structured prompt scopes the reason.

You give a one-liner; Cursor writes the doc back at you. You don't author docs by hand. Examples:

```
/eg-brainstorm [BOOTSTRAP: a short, realistic raw idea for this project — "what if we let users X" sort of thing]
/eg-prd [BOOTSTRAP: a short, realistic feature you'd want a PRD for — "an export-to-CSV button on the SKU list" sort of thing]
/eg-fix-bug [BOOTSTRAP: a short, realistic bug description for this project]
/eg-fix-bug #123
/eg-new-feature [BOOTSTRAP: a short, realistic feature description for this project]
/eg-precommit-review
```

[BOOTSTRAP: browser validation paragraph — choose one:
- For web apps: "Browser validation: use Cursor's built-in `browser` subagent (Browser MCP) pointed at the dev server on `[BOOTSTRAP: dev URL]`. Start the server via `[BOOTSTRAP: dev start command]` if it isn't already running."
- For mobile: "Verification: primary path is a real simulator/device run (`flutter run -d ios`, etc.). For layout-only behavior that reproduces on web, `flutter run -d chrome` plus the `browser` subagent can be used."
- For backend-only: omit this paragraph.]

Each skill stops short of committing. Authorize the commit explicitly when ready. [BOOTSTRAP: commit-policy reminder if the project has one — e.g. "Squash-merge with Conventional Commits; no AI co-author trailers."]

**These skills are interactive by design.** `AskQuestion` gates inside `/eg-brainstorm`, `/eg-prd`, `/eg-fix-bug`, `/eg-new-feature`, and `/eg-precommit-review` are part of the skill's protocol and run even when a directive in this session asks Cursor to work autonomously without clarifying questions. If you want a fully autonomous pass on a specific run, say "skip the framing questions and use defaults" in the same turn that invokes the skill; each skill documents which gates remain non-negotiable.
<<<SNIPPET_END>>>
```
