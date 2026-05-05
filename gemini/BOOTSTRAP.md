# Gemini CLI BOOTSTRAP.md

This file is read by Gemini CLI. The user has pointed you at this repo and asked you to set up the elephant/goldfish workflow in their target repo. Follow these steps.

## How to fetch the rest of this repo's content

There is no local working copy on the target machine — you got here by streaming this file's text through `gh api`. Fetch the remaining files (the five skill templates and the GEMINI.md snippet) the same way, on demand:

```sh
gh api repos/vshvedov/elephant-goldfish/contents/<PATH> -H 'Accept: application/vnd.github.raw'
```

Files this procedure references later:

- `gemini/commands/eg-brainstorm.md`
- `gemini/commands/eg-prd.md`
- `gemini/commands/eg-fix-bug.md`
- `gemini/commands/eg-new-feature.md`
- `gemini/commands/eg-precommit-review.md`
- `gemini/gemini-md-snippet.md`

Recommended: fetch them all up front into a tmp dir, then read locally through the rest of the steps:

```sh
mkdir -p /tmp/elephant-goldfish/gemini/commands
for f in gemini/gemini-md-snippet.md gemini/commands/eg-brainstorm.md gemini/commands/eg-prd.md gemini/commands/eg-fix-bug.md gemini/commands/eg-new-feature.md gemini/commands/eg-precommit-review.md; do
  gh api "repos/vshvedov/elephant-goldfish/contents/${f}" -H 'Accept: application/vnd.github.raw' > "/tmp/elephant-goldfish/${f}"
done
```

After this, every reference to `gemini/commands/<name>.md` or `gemini/gemini-md-snippet.md` below resolves to `/tmp/elephant-goldfish/<same path>` in your local read.

## Step 0: Confirm the target

The user invoked you from a working directory that is the target repo. Confirm: print the target's absolute path and ask the user to confirm before doing anything destructive. If the target already has any of `.gemini/skills/{eg-brainstorm,eg-prd,eg-fix-bug,eg-new-feature,eg-precommit-review}`, ask whether to overwrite, augment, or abort.

## Step 1: Inspect the stack

Read these files in the target if they exist (parallel reads):

- `GEMINI.md` (top of repo) — existing conventions, commit policy, PR workflow, tooling notes
- `package.json` → `scripts`, `dependencies`, `devDependencies` (Node / web stacks)
- `Gemfile` → linter, test framework, security scanner (Rails / Ruby)
- `pubspec.yaml` → Flutter / Dart
- `pyproject.toml` / `requirements.txt` / `setup.py` / `Pipfile` (Python)
- `go.mod` (Go), `Cargo.toml` (Rust), `composer.json` (PHP), `mix.exs` (Elixir)
- `tsconfig.json`, `playwright.config.ts`, `vitest.config.ts`, `jest.config.js`, etc.
- `Rakefile`, `Makefile`, `justfile`, `mise.toml`, `.tool-versions`, `.nvmrc`, `.ruby-version`
- `docker-compose.yml`, `Dockerfile` (for dev-server entrypoints)
- `.github/workflows/*.yml` (the CI commands tell you what the project considers "passing")

Also `git log --oneline -10` to learn the commit-message convention.

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
- Code-generation step required before tests (build_runner, protoc, codegen) + when:
- Existing PR workflow, code review process, or merge gates documented in GEMINI.md:
- Commit message convention from `git log`:
- Multi-tenancy / auth / scoping concerns the reviewer should always check:
- Stack-specific gotchas (N+1 in Rails, dispose in Flutter, audio-thread allocs in real-time, hydration in Next, etc.):
```

Print the stack profile to the user and ask them to confirm or correct before generating the commands. Misreads here propagate downstream.

## Step 2: Generate the five skill packages

Use the fetched markdown files as skeletons. Substitute every `[BOOTSTRAP: ...]` marker with concrete values from the stack profile.

`eg-brainstorm.md` and `eg-prd.md` are mostly stack-agnostic by design — each carries one or two `[BOOTSTRAP: ...]` markers for save paths. Pick sensible defaults for the target:

- `eg-brainstorm.md` save path: `docs/eg-brainstorms/<slug>-<YYYY-MM-DD>.md` if there's a `docs/` tree, otherwise `notes/eg-brainstorms/...`.
- `eg-prd.md` save path: `docs/prds/<slug>-<YYYY-MM-DD>.md` if there's a `docs/` tree, otherwise `docs/specs/...` or `notes/prds/...`. If the project already has a PRD location, use that.

Specifically:
- `[BOOTSTRAP: lint command]` → the actual command (e.g. `npm run lint`, `flutter analyze`).
- `[BOOTSTRAP: typecheck command]` → the actual command, or remove the bullet entirely.
- `[BOOTSTRAP: unit test command]`, `[BOOTSTRAP: e2e test command]` → as observed.
- `[BOOTSTRAP: dev server URL]` → e.g. `http://localhost:3000`.
- `[BOOTSTRAP: test tier picks]` → match the actual test folder layout in the target. List the concrete folders.
- `[BOOTSTRAP: stack-specific Hunt for items]` → ADD bullets to the reviewer's "Hunt for" list. Be concrete based on the stack (e.g., N+1 queries for Rails, state disposal for Flutter, etc.).
- `[BOOTSTRAP: project-specific routing note]` → if the project has a stack-specific verb, reference it so users know when to switch.
- `[BOOTSTRAP: commit message style note]` → the convention observed in `git log`.

## Step 3: Write and Install the Skills

For each of the five workflows (eg-brainstorm, eg-prd, eg-fix-bug, eg-new-feature, eg-precommit-review):

1. Create the skill directory: `mkdir -p .gemini/skills/<skill-name>`
2. Write the fully substituted template to `.gemini/skills/<skill-name>/SKILL.md`
3. Automatically install the skill in the workspace using the `run_shell_command` tool:
   ```sh
   gemini skills install .gemini/skills/<skill-name> --scope workspace
   ```

## Step 4: Update GEMINI.md

Read the snippet from your prefetched copy at `/tmp/elephant-goldfish/gemini/gemini-md-snippet.md`. Tailor the placeholders in it to match the target's setup and inject it into the target's `GEMINI.md`.

- If the target already has a `GEMINI.md`, inject the snippet near the top.
- If no `GEMINI.md` exists, propose creating one and ask the user before writing.

## Step 5: Sanity-check the output

For each generated `SKILL.md` file:
- Ensure the YAML frontmatter (`name`, `description`) is intact at the very top.
- No `[BOOTSTRAP: ...]` markers remaining.
- Commands referenced actually exist in the target.
- The reviewer template's `<<<TEMPLATE_START>>> ... <<<TEMPLATE_END>>>` markers and the diagnosis/design markers are intact and unmodified.

## Step 6: Final report

Print to the user:
- Stack profile (confirmed or corrected by user)
- Skill packages created and installed locally
- GEMINI.md change
- Anything you couldn't infer
- **IMPORTANT:** Instruct the user that they must run `/skills reload` in their interactive Gemini CLI session to activate the newly installed skills.

**Stop short of committing.** The user authorizes the commit when ready, following the target's commit convention.

## Re-bootstrapping

When the user says "re-bootstrap" or "update the skills from the template repo," do the same flow but **diff against the existing files** before overwriting. Preserve any project-specific edits the user made to their `SKILL.md` files. After overwriting, reinstall them.
