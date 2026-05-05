# Claude Code BOOTSTRAP.md

This file is read by Claude Code. The user has pointed you at this repo and asked you to set up the elephant/goldfish workflow in their target repo. Follow these steps.

## How to fetch the rest of this repo's content

There is no local working copy on the target machine — you got here by streaming this file's text through `gh api`. Fetch the remaining files (the five command templates and the CLAUDE.md snippet) the same way, on demand:

```sh
gh api repos/vshvedov/elephant-goldfish/contents/<PATH> -H 'Accept: application/vnd.github.raw'
```

Files this procedure references later:

- `claude/commands/eg-brainstorm.md`
- `claude/commands/eg-prd.md`
- `claude/commands/eg-fix-bug.md`
- `claude/commands/eg-new-feature.md`
- `claude/commands/eg-precommit-review.md`
- `claude/claude-md-snippet.md`

Recommended: fetch them all up front into a tmp dir, then read locally through the rest of the steps:

```sh
mkdir -p /tmp/elephant-goldfish/claude/commands
for f in claude/claude-md-snippet.md claude/commands/eg-brainstorm.md claude/commands/eg-prd.md claude/commands/eg-fix-bug.md claude/commands/eg-new-feature.md claude/commands/eg-precommit-review.md; do
  gh api "repos/vshvedov/elephant-goldfish/contents/${f}" -H 'Accept: application/vnd.github.raw' > "/tmp/elephant-goldfish/${f}"
done
```

After this, every reference to `claude/commands/<name>.md` or `claude/claude-md-snippet.md` below resolves to `/tmp/elephant-goldfish/<same path>` in your local read.

## Step 0: Confirm the target

The user invoked you from a working directory that is the target repo. Confirm: print the target's absolute path and ask the user to confirm before doing anything destructive. If the target already has any of `.claude/commands/{eg-brainstorm,eg-prd,eg-fix-bug,eg-new-feature,eg-precommit-review}.md`, ask whether to overwrite, augment, or abort.

## Step 1: Inspect the stack

Read these files in the target if they exist (parallel reads):

- `CLAUDE.md` (top of repo) — existing conventions, commit policy, PR workflow, tooling notes
- `package.json` → `scripts`, `dependencies`, `devDependencies` (Node / web stacks)
- `Gemfile` → linter, test framework, security scanner (Rails / Ruby)
- `pubspec.yaml` → Flutter / Dart
- `pyproject.toml` / `requirements.txt` / `setup.py` / `Pipfile` (Python)
- `go.mod` (Go), `Cargo.toml` (Rust), `composer.json` (PHP), `mix.exs` (Elixir)
- `tsconfig.json`, `playwright.config.ts`, `vitest.config.ts`, `jest.config.js`, etc.
- `Rakefile`, `Makefile`, `justfile`, `mise.toml`, `.tool-versions`, `.nvmrc`, `.ruby-version`
- `docker-compose.yml`, `Dockerfile` (for dev-server entrypoints)
- `.github/workflows/*.yml` (the CI commands tell you what the project considers "passing")

Also `git log --oneline -10` to learn the commit-message convention (subject style, ticket references, trailers).

From this, derive a **stack profile**:

```
STACK PROFILE
- Language(s) and framework(s):
- Package manager + version manager (mise / asdf / nvm / rbenv / etc.):
- Linter + how to invoke:
- Type-checker + how to invoke (or "n/a"):
- Unit/integration test runner + how to invoke:
- E2E test runner + how to invoke (or "n/a"):
- Security scanner + how to invoke (or "n/a"):
- Dev server: command + URL:
- Browser validation strategy: Chrome MCP path (URL), simulator/device runs (mobile), or n/a (pure backend)
- Code-generation step required before tests (build_runner, protoc, codegen) + when:
- Existing PR workflow, code review process, or merge gates documented in CLAUDE.md:
- Commit message convention from `git log`:
- Multi-tenancy / auth / scoping concerns the reviewer should always check:
- Stack-specific gotchas (N+1 in Rails, dispose in Flutter, audio-thread allocs in real-time, hydration in Next, etc.):
```

Print the stack profile to the user and ask them to confirm or correct before generating the commands. Misreads here propagate downstream.

## Step 2: Generate the five commands

Use `claude/commands/eg-fix-bug.md`, `claude/commands/eg-new-feature.md`, `claude/commands/eg-precommit-review.md`, `claude/commands/eg-brainstorm.md`, and `claude/commands/eg-prd.md` as the skeletons. Substitute every `[BOOTSTRAP: ...]` marker with concrete values from the stack profile.

`eg-brainstorm.md` and `eg-prd.md` are mostly stack-agnostic by design (they produce concepts and requirements, not code) — each carries one or two `[BOOTSTRAP: ...]` markers for save paths. Pick sensible defaults for the target:

- `eg-brainstorm.md` save path: `docs/eg-brainstorms/<slug>-<YYYY-MM-DD>.md` if there's a `docs/` tree, otherwise `notes/eg-brainstorms/...`.
- `eg-prd.md` save path: `docs/prds/<slug>-<YYYY-MM-DD>.md` if there's a `docs/` tree, otherwise `docs/specs/...` or `notes/prds/...`. If the project already has a PRD location (look for `docs/prds/`, `docs/specs/`, `prd/`, or a PRD listed in CLAUDE.md), use that.

Specifically:
- `[BOOTSTRAP: lint command]` → the actual command (e.g. `npm run lint`, `mise exec ruby@2.7.5 -- bundle exec rubocop`, `flutter analyze`).
- `[BOOTSTRAP: typecheck command]` → the actual command, or remove the bullet entirely if the language has no separate type-check step.
- `[BOOTSTRAP: unit test command]`, `[BOOTSTRAP: e2e test command]` → as observed.
- `[BOOTSTRAP: dev server URL]` → e.g. `http://localhost:3000`, `https://localhost:4444`.
- `[BOOTSTRAP: browser validation block]` → either Chrome MCP instructions for a web app, simulator/device run instructions for mobile, or "n/a — backend-only" with the block removed.
- `[BOOTSTRAP: test tier picks]` → match the actual test folder layout in the target. List the concrete folders (e.g. `test/models/`, `test/system/`, `e2e/`).
- `[BOOTSTRAP: stack-specific Hunt for items]` → ADD bullets to the reviewer's "Hunt for" list. Examples by stack:
  - **Rails:** N+1 queries, missing `includes`, mass assignment, missing CanCanCan auth, multi-tenant scoping, Sidekiq idempotency, Grape API drift, raw SQL, callback ordering.
  - **Node + Solid/React/Vue:** signal-accessor scope, missing `<For>` keys, missing effect cleanup, stale closures over signals, hydration mismatch in SSR, missing `await` on promises, `unknown` cast as `any`.
  - **Flutter:** stream/controller dispose, BLoC race with dispose, Provider scope mismatch, `setState` after dispose, missing `const` constructors, platform divergence (iOS / Android / macOS), Drift schema migration `schemaVersion` bump, generated `.g.dart` drift.
  - **Cloudflare Workers:** request-scope leaks, D1 transaction semantics, R2 binding misuse, missing rate limiting on auth endpoints, exposing internal IDs, COOP/COEP header regressions.
  - **Real-time audio / DSP:** allocations in `process()`, lock-free invariants, parameter smoothing, sample-rate assumptions, NaN/Inf safety.
  - **Python web (Django/FastAPI/Flask):** N+1 (`select_related`/`prefetch_related`), CSRF, SQLAlchemy session leaks, async/sync mixing, Pydantic validation drift.
  - **Mobile (general):** background-task lifecycle, memory leaks via retain cycles, app-backgrounded state restoration.
  - Add others as appropriate. Be concrete, not generic.
- `[BOOTSTRAP: project-specific routing note]` → if the project has a stack-specific verb (e.g. `/eg-new-module`), reference it in `/eg-new-feature.md`'s opening so users know when to switch. Skip if no such verb exists yet. Project-specific commands should also carry the `eg-` prefix to keep the namespace consistent.
- `[BOOTSTRAP: commit message style note]` → the convention observed in `git log`.

The base "Hunt for" list (universal items: bugs, security, race conditions, edge cases, error handling, performance, test-coverage gaps, dead code) stays as-is. You're appending stack-specific items, not replacing.

## Step 3: Write the files

Create `<target>/.claude/commands/{eg-brainstorm,eg-prd,eg-fix-bug,eg-new-feature,eg-precommit-review}.md` from the substituted templates. If the directory doesn't exist, create it.

## Step 4: Update CLAUDE.md

Read `claude/claude-md-snippet.md`. Tailor the placeholders in it to match the target's setup (dev URL, project-specific commands if any) and inject it into the target's `CLAUDE.md`.

- If the target already has a `CLAUDE.md`, inject the snippet near the top (after the project overview, before existing workflow sections).
- If no `CLAUDE.md` exists, propose creating one and ask the user before writing. Seed it with: project overview placeholder, the snippet, and a stub for build/test commands.

## Step 5: Sanity-check the output

For each generated file:
- No `[BOOTSTRAP: ...]` markers remaining.
- Commands referenced actually exist in the target (e.g. don't reference `npm test` if there's no `test` script).
- File paths in test-tier picks correspond to real folders.
- The reviewer template's `<<<TEMPLATE_START>>> ... <<<TEMPLATE_END>>>` markers and the diagnosis/design markers are intact and unmodified.

## Step 6: Final report

Print to the user:
- Stack profile (confirmed or corrected by user)
- Files created (with paths)
- CLAUDE.md change (created or updated, with the section title)
- Anything you couldn't infer and want the user to fill in (e.g. "no E2E framework detected — `/eg-precommit-review` will skip that tier; tell me if you want it added")
- Project-specific commands worth considering next (e.g. "this is a Rails app with Sidekiq workers — consider a `/new-worker` if you create them often")

**Stop short of committing.** The user authorizes the commit when ready, following the target's commit convention.

## Re-bootstrapping

When the user says "re-bootstrap" or "update the commands from the template repo," do the same flow but **diff against the existing files** before overwriting:
- Show the user what changed in each command.
- Preserve any project-specific edits the user made (look for content that is not in the generic template — Playwright fallback notes, custom phase gates, project-specific bullets).
- Ask before overwriting if any preserved edits would be lost.
