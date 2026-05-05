# Snippet to inject into target CLAUDE.md

This is the section that gets added to the target repo's `CLAUDE.md` during bootstrap. Tailor the placeholders, then inject. Do not include this header line or the surrounding text — only what's between the `<<<SNIPPET_START>>>` and `<<<SNIPPET_END>>>` markers.

```
<<<SNIPPET_START>>>
## Working with Claude Code (slash commands)

Five slash commands in [.claude/commands/](.claude/commands/) wrap an "elephant/goldfish" workflow inspired by [this article](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874): the "elephant" is the working session with full context (this CLAUDE.md, repo state, conversation history); the "goldfish" is a fresh subagent with no prior context. For implementation work the goldfish stress-tests a problem/design doc or a diff. For brainstorming and PRD writing, multiple goldfish run in parallel with different lenses to generate divergent ideas or research findings the elephant synthesizes.

| Command | When to use |
|---|---|
| `/eg-brainstorm <rough idea>` | Early-stage concept design. Multiple goldfish in parallel (technical / business / UX / contrarian / market research), web search optional, elephant synthesizes a concepts brief. All questions via `AskUserQuestion`. Hands off to `/eg-prd` or `/eg-new-feature` if you pick a direction. |
| `/eg-prd <idea \| feature description>` | Build a thorough PRD: codebase grounding → structured gap-filling via `AskUserQuestion` → deep research with parallel goldfish (web + optional Chrome MCP for logged-in sources) → synthesized PRD. Saves to `[BOOTSTRAP: prd path, e.g. `docs/prds/`]`, persists durable nuggets to memory, and/or hands off to `/eg-new-feature`. |
| `/eg-fix-bug <description \| #issue \| URL>` | Bug fix flow: problem doc → goldfish diagnosis check → failing test → fix → `/eg-precommit-review` → test gate. Skips ceremony for trivial diffs. |
| `/eg-new-feature <description \| #issue \| URL>` | Feature flow: scope confirm → design doc → goldfish design check → implement → `/eg-precommit-review` → test gate. [BOOTSTRAP: one-line summary of stack-specific design rubric items, e.g. "Multi-tenant scoping and CanCanCan checks are part of the design rubric." for Rails, or "Lifecycle/dispose, BLoC scope, cache invalidation, and platform-divergence checks." for Flutter.] |
| `/eg-precommit-review` | Local independent-review loop on the pending diff ([BOOTSTRAP: pre-flight summary, e.g. "Brakeman + MiniTest + Playwright"]). Replaces back-and-forth with PR bots — by the time the PR opens, the substantive review is already settled. |
[BOOTSTRAP: if the project has a stack-specific verb like `/eg-new-module`, add a row for it here.]

You give a one-liner; Claude writes the doc back at you. You don't author docs by hand. Examples:

```
/eg-brainstorm [BOOTSTRAP: a short, realistic raw idea for this project — "what if we let users X" sort of thing]
/eg-prd [BOOTSTRAP: a short, realistic feature you'd want a PRD for — "an export-to-CSV button on the SKU list" sort of thing]
/eg-fix-bug [BOOTSTRAP: a short, realistic bug description for this project]
/eg-fix-bug #123
/eg-new-feature [BOOTSTRAP: a short, realistic feature description for this project]
/eg-precommit-review
```

[BOOTSTRAP: browser validation paragraph — choose one:
- For web apps: "Browser validation: use the Claude in Chrome MCP (`mcp__Claude_in_Chrome__*`) pointed at the dev server on `[BOOTSTRAP: dev URL]`. Start the server via `[BOOTSTRAP: dev start command]` if it isn't already running."
- For mobile: "Verification: primary path is a real simulator/device run (`flutter run -d ios`, etc.). For layout-only behavior that reproduces on web, `flutter run -d chrome` plus the Chrome MCP can be used."
- For backend-only: omit this paragraph.]

Each command stops short of committing. Authorize the commit explicitly when ready. [BOOTSTRAP: commit-policy reminder if the project has one — e.g. "No `Co-Authored-By: Claude` trailers in commit messages."]
<<<SNIPPET_END>>>
```
